"""
Demo data for prototype presentations: levels, courses, lessons with content for all five skills,
and two users (one onboarded with progress, one fresh for the onboarding flow).

    make seed            # refuses to run twice
    make seed-reset      # wipes everything except skills, then seeds again
"""

import asyncio
import random
import sys
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select, text

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models import (
    ActivityLog,
    Course,
    Dialogue,
    DialogueExchange,
    KanjiPractice,
    LearnerProfile,
    Lesson,
    ListeningPractice,
    ListeningQuestion,
    ListeningQuestionOption,
    ProficiencyLevel,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionOption,
    Skill,
    User,
    Vocabulary,
    VocabularyReview,
)

LEVELS = ["N5", "N4", "N3"]  # JLPT names: the client looks levels up by name

# Each question is (text, [options], index of the correct option).
LESSONS = [
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Greetings & Introductions",
        "content": "Learn how to greet people and introduce yourself in Japanese.",
        "vocab": [
            (None, "こんにちは", "konnichiwa", "hello / good afternoon", "こんにちは、田中さん。", "Hello, Mr. Tanaka."),
            (None, "おはよう", "ohayou", "good morning", "おはよう、ママ。", "Good morning, Mom."),
            (None, "こんばんは", "konbanwa", "good evening", "こんばんは、みなさん。", "Good evening, everyone."),
            (None, "ありがとう", "arigatou", "thank you", "どうもありがとう。", "Thank you very much."),
            ("名前", "なまえ", "namae", "name", "お名前は何ですか。", "What is your name?"),
            ("私", "わたし", "watashi", "I / me", "私は学生です。", "I am a student."),
            ("学生", "がくせい", "gakusei", "student", "彼は学生です。", "He is a student."),
            ("先生", "せんせい", "sensei", "teacher", "山田先生はやさしいです。", "Professor Yamada is kind."),
        ],
        "reading": {
            "title": "はじめまして",
            "ja": "はじめまして。私はアンです。ベトナムから来ました。大学の学生です。日本語を勉強しています。どうぞよろしくお願いします。",
            "vi": "Xin chào. Tôi là An. Tôi đến từ Việt Nam. Tôi là sinh viên đại học. Tôi đang học tiếng Nhật. Rất mong được giúp đỡ.",
            "questions": [
                ("アンさんはどこから来ましたか。", ["日本", "ベトナム", "中国", "アメリカ"], 1),
                ("アンさんは何ですか。", ["先生", "医者", "学生", "会社員"], 2),
                ("アンさんは何を勉強していますか。", ["英語", "日本語", "数学", "音楽"], 1),
            ],
        },
        "dialogue": {
            "title": "Meeting a classmate",
            "description": "Introduce yourself to a new classmate on the first day.",
            "exchanges": [
                ("A", "はじめまして。田中です。", "Hajimemashite. Tanaka desu.", "Nice to meet you. I'm Tanaka."),
                ("B", "はじめまして。アンです。", "Hajimemashite. An desu.", "Nice to meet you. I'm An."),
                ("A", "アンさんはどこから来ましたか。", "An-san wa doko kara kimashita ka.", "Where are you from, An?"),
                ("B", "ベトナムから来ました。", "Betonamu kara kimashita.", "I'm from Vietnam."),
                ("A", "よろしくお願いします。", "Yoroshiku onegaishimasu.", "Nice to meet you (please treat me well)."),
                ("B", "こちらこそ、よろしく。", "Kochira koso, yoroshiku.", "Likewise."),
            ],
        },
        "kanji": [("Person", "人", "easy"), ("Sun / day", "日", "easy"), ("Book / origin", "本", "easy")],
        "listening": {
            "title": "Morning greetings",
            "source_type": "dialogue",
            "ja": "A: おはようございます。\nB: おはようございます。今日はいい天気ですね。\nA: そうですね。",
            "vi": "A: Chào buổi sáng.\nB: Chào buổi sáng. Hôm nay trời đẹp nhỉ.\nA: Đúng vậy.",
            "questions": [
                ("What time of day is it?", ["Morning", "Afternoon", "Evening", "Night"], 0),
                ("How is the weather?", ["Rainy", "Nice", "Cold", "Windy"], 1),
            ],
        },
    },
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Numbers & Counting",
        "content": "Count from one to ten and ask how much something costs.",
        "vocab": [
            ("一", "いち", "ichi", "one", "りんごを一つください。", "One apple, please."),
            ("二", "に", "ni", "two", "二人で行きます。", "We'll go as two people."),
            ("三", "さん", "san", "three", "三時に会いましょう。", "Let's meet at three."),
            ("四", "よん", "yon", "four", "四月です。", "It's April."),
            ("五", "ご", "go", "five", "五分待ってください。", "Please wait five minutes."),
            ("十", "じゅう", "juu", "ten", "十円です。", "It's ten yen."),
            ("百", "ひゃく", "hyaku", "hundred", "百円ショップ。", "Hundred-yen shop."),
            (None, "いくら", "ikura", "how much", "これはいくらですか。", "How much is this?"),
        ],
        "reading": {
            "title": "コンビニで",
            "ja": "私はコンビニに行きました。おにぎりを二つとお茶を一本買いました。全部で三百円でした。",
            "vi": "Tôi đã đi đến cửa hàng tiện lợi. Tôi mua hai cơm nắm và một chai trà. Tổng cộng là ba trăm yên.",
            "questions": [
                ("おにぎりをいくつ買いましたか。", ["一つ", "二つ", "三つ", "四つ"], 1),
                ("全部でいくらでしたか。", ["百円", "二百円", "三百円", "五百円"], 2),
            ],
        },
        "dialogue": {
            "title": "At the convenience store",
            "description": "Buy a snack and ask for the price.",
            "exchanges": [
                ("Clerk", "いらっしゃいませ。", "Irasshaimase.", "Welcome."),
                ("You", "これはいくらですか。", "Kore wa ikura desu ka.", "How much is this?"),
                ("Clerk", "百五十円です。", "Hyaku gojuu en desu.", "It's 150 yen."),
                ("You", "じゃあ、これをください。", "Jaa, kore o kudasai.", "Then I'll take this."),
            ],
        },
        "kanji": [("One", "一", "easy"), ("Two", "二", "easy"), ("Three", "三", "easy"), ("Ten", "十", "easy")],
        "listening": {
            "title": "Phone numbers",
            "source_type": "sentences",
            "ja": "電話番号は、ゼロ・キュウ・ゼロ、イチ・ニ・サン・ヨン、ゴ・ロク・ナナ・ハチです。",
            "vi": "Số điện thoại là 090-1234-5678.",
            "questions": [("Which number did you hear?", ["090-1234-5678", "080-1234-5678", "090-4321-8765", "070-1234-5678"], 0)],
        },
    },
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Family",
        "content": "Talk about your family members.",
        "vocab": [
            ("家族", "かぞく", "kazoku", "family", "家族は四人です。", "There are four people in my family."),
            ("父", "ちち", "chichi", "(my) father", "父は会社員です。", "My father is an office worker."),
            ("母", "はは", "haha", "(my) mother", "母は料理が上手です。", "My mother is good at cooking."),
            ("兄", "あに", "ani", "(my) older brother", "兄は東京にいます。", "My older brother is in Tokyo."),
            ("姉", "あね", "ane", "(my) older sister", "姉は先生です。", "My older sister is a teacher."),
            ("弟", "おとうと", "otouto", "younger brother", "弟は十歳です。", "My younger brother is ten."),
        ],
        "reading": {
            "title": "私の家族",
            "ja": "私の家族は五人です。父と母と兄と妹と私です。父は医者です。母は先生です。兄は大学生です。",
            "vi": "Gia đình tôi có năm người: bố, mẹ, anh trai, em gái và tôi. Bố là bác sĩ. Mẹ là giáo viên. Anh trai là sinh viên đại học.",
            "questions": [
                ("家族は何人ですか。", ["三人", "四人", "五人", "六人"], 2),
                ("お父さんの仕事は何ですか。", ["先生", "医者", "学生", "会社員"], 1),
                ("お兄さんは何ですか。", ["大学生", "高校生", "先生", "医者"], 0),
            ],
        },
        "dialogue": {
            "title": "Family photo",
            "description": "Show a friend a photo of your family.",
            "exchanges": [
                ("A", "これは家族の写真ですか。", "Kore wa kazoku no shashin desu ka.", "Is this a photo of your family?"),
                ("B", "はい、そうです。", "Hai, sou desu.", "Yes, it is."),
                ("A", "この人はだれですか。", "Kono hito wa dare desu ka.", "Who is this person?"),
                ("B", "姉です。先生です。", "Ane desu. Sensei desu.", "My older sister. She's a teacher."),
            ],
        },
        "kanji": [("Father", "父", "medium"), ("Mother", "母", "medium"), ("Child", "子", "easy")],
        "listening": {
            "title": "How many siblings?",
            "source_type": "dialogue",
            "ja": "A: 兄弟がいますか。\nB: はい、姉が一人と弟が二人います。",
            "vi": "A: Bạn có anh chị em không?\nB: Có, tôi có một chị gái và hai em trai.",
            "questions": [
                ("How many younger brothers does B have?", ["None", "One", "Two", "Three"], 2),
                ("Does B have an older sister?", ["Yes, one", "Yes, two", "No", "Not mentioned"], 0),
            ],
        },
    },
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Food & Restaurants",
        "content": "Order food and talk about what you like to eat.",
        "vocab": [
            ("水", "みず", "mizu", "water", "水をください。", "Water, please."),
            ("お茶", "おちゃ", "ocha", "tea", "お茶を飲みます。", "I drink tea."),
            ("ご飯", "ごはん", "gohan", "rice / meal", "ご飯を食べましょう。", "Let's eat."),
            ("魚", "さかな", "sakana", "fish", "魚が好きです。", "I like fish."),
            ("肉", "にく", "niku", "meat", "肉は食べません。", "I don't eat meat."),
            (None, "おいしい", "oishii", "delicious", "このラーメンはおいしいです。", "This ramen is delicious."),
            ("食べる", "たべる", "taberu", "to eat", "寿司を食べます。", "I eat sushi."),
        ],
        "reading": {
            "title": "ラーメン屋",
            "ja": "昨日、友達とラーメン屋に行きました。私はしょうゆラーメンを食べました。友達はみそラーメンを食べました。とてもおいしかったです。",
            "vi": "Hôm qua tôi đã đi quán ramen với bạn. Tôi ăn ramen shoyu. Bạn tôi ăn ramen miso. Rất ngon.",
            "questions": [
                ("いつラーメン屋に行きましたか。", ["今日", "昨日", "明日", "先週"], 1),
                ("友達は何を食べましたか。", ["しょうゆラーメン", "みそラーメン", "寿司", "カレー"], 1),
            ],
        },
        "dialogue": {
            "title": "Ordering at a restaurant",
            "description": "Order a meal and a drink.",
            "exchanges": [
                ("Waiter", "ご注文は?", "Go-chuumon wa?", "What would you like to order?"),
                ("You", "カレーライスをお願いします。", "Karee raisu o onegaishimasu.", "Curry rice, please."),
                ("Waiter", "お飲み物は?", "O-nomimono wa?", "Anything to drink?"),
                ("You", "お水をください。", "O-mizu o kudasai.", "Water, please."),
                ("Waiter", "かしこまりました。", "Kashikomarimashita.", "Certainly."),
            ],
        },
        "kanji": [("Water", "水", "easy"), ("Eat", "食", "hard"), ("Fish", "魚", "hard")],
        "listening": {
            "title": "What do you want to eat?",
            "source_type": "dialogue",
            "ja": "A: 何を食べたいですか。\nB: 寿司が食べたいです。\nA: いいですね。駅の近くにおいしい店がありますよ。",
            "vi": "A: Bạn muốn ăn gì?\nB: Tôi muốn ăn sushi.\nA: Hay đấy. Gần ga có một quán ngon.",
            "questions": [
                ("What does B want to eat?", ["Ramen", "Sushi", "Curry", "Tempura"], 1),
                ("Where is the restaurant?", ["Near the station", "Near the school", "At home", "In the park"], 0),
            ],
        },
    },
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Time & Daily Routine",
        "content": "Tell the time and describe your day.",
        "vocab": [
            ("今", "いま", "ima", "now", "今、何時ですか。", "What time is it now?"),
            ("時", "じ", "ji", "o'clock", "七時に起きます。", "I get up at seven."),
            ("毎日", "まいにち", "mainichi", "every day", "毎日勉強します。", "I study every day."),
            ("朝", "あさ", "asa", "morning", "朝ご飯を食べます。", "I eat breakfast."),
            ("夜", "よる", "yoru", "night", "夜は本を読みます。", "I read books at night."),
            ("起きる", "おきる", "okiru", "to wake up", "六時に起きました。", "I woke up at six."),
        ],
        "reading": {
            "title": "私の一日",
            "ja": "私は毎朝六時に起きます。七時に朝ご飯を食べて、八時に学校へ行きます。夜は十一時に寝ます。",
            "vi": "Mỗi sáng tôi dậy lúc sáu giờ. Bảy giờ tôi ăn sáng và tám giờ đi học. Buổi tối tôi ngủ lúc mười một giờ.",
            "questions": [
                ("何時に起きますか。", ["五時", "六時", "七時", "八時"], 1),
                ("何時に寝ますか。", ["九時", "十時", "十一時", "十二時"], 2),
            ],
        },
        "dialogue": {
            "title": "Making plans",
            "description": "Agree on a time to meet a friend.",
            "exchanges": [
                ("A", "明日、時間がありますか。", "Ashita, jikan ga arimasu ka.", "Do you have time tomorrow?"),
                ("B", "はい、午後は大丈夫です。", "Hai, gogo wa daijoubu desu.", "Yes, the afternoon is fine."),
                ("A", "じゃあ、三時に駅で会いましょう。", "Jaa, sanji ni eki de aimashou.", "Then let's meet at the station at three."),
                ("B", "わかりました。", "Wakarimashita.", "Got it."),
            ],
        },
        "kanji": [("Time / hour", "時", "medium"), ("Now", "今", "medium"), ("Morning", "朝", "hard")],
        "listening": {
            "title": "Train announcement",
            "source_type": "sentences",
            "ja": "まもなく、三番線に八時十五分発の電車がまいります。",
            "vi": "Sắp tới, tàu khởi hành lúc 8 giờ 15 sẽ đến sân ga số 3.",
            "questions": [
                ("What time does the train leave?", ["8:05", "8:15", "8:50", "3:15"], 1),
                ("Which platform?", ["1", "2", "3", "8"], 2),
            ],
        },
    },
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Shopping",
        "content": "Shop for clothes and ask for different sizes and colors.",
        "vocab": [
            ("買う", "かう", "kau", "to buy", "新しい靴を買いました。", "I bought new shoes."),
            ("高い", "たかい", "takai", "expensive / tall", "このかばんは高いです。", "This bag is expensive."),
            ("安い", "やすい", "yasui", "cheap", "あの店は安いです。", "That shop is cheap."),
            ("赤い", "あかい", "akai", "red", "赤いシャツがほしいです。", "I want a red shirt."),
            ("大きい", "おおきい", "ookii", "big", "もっと大きいのはありますか。", "Do you have a bigger one?"),
            ("小さい", "ちいさい", "chiisai", "small", "これは小さすぎます。", "This is too small."),
        ],
        "reading": {
            "title": "デパートで",
            "ja": "週末、デパートへ買い物に行きました。青いセーターがほしかったですが、高すぎました。それで、安いTシャツを二枚買いました。",
            "vi": "Cuối tuần tôi đi mua sắm ở trung tâm thương mại. Tôi muốn mua áo len màu xanh nhưng quá đắt. Vì vậy tôi mua hai chiếc áo phông rẻ.",
            "questions": [
                ("何がほしかったですか。", ["赤いシャツ", "青いセーター", "黒いくつ", "白いかばん"], 1),
                ("どうしてセーターを買いませんでしたか。", ["小さかった", "高すぎた", "色が悪かった", "店が閉まっていた"], 1),
                ("何を買いましたか。", ["セーター", "Tシャツ二枚", "くつ", "何も買わなかった"], 1),
            ],
        },
        "dialogue": {
            "title": "Trying on clothes",
            "description": "Ask a shop assistant for a different size.",
            "exchanges": [
                ("You", "すみません、これを着てみてもいいですか。", "Sumimasen, kore o kite mite mo ii desu ka.", "Excuse me, may I try this on?"),
                ("Staff", "はい、どうぞ。試着室はあちらです。", "Hai, douzo. Shichakushitsu wa achira desu.", "Sure. The fitting room is over there."),
                ("You", "ちょっと小さいです。Lサイズはありますか。", "Chotto chiisai desu. L saizu wa arimasu ka.", "It's a little small. Do you have a large?"),
                ("Staff", "少々お待ちください。", "Shoushou omachi kudasai.", "One moment, please."),
            ],
        },
        "kanji": [("Buy", "買", "hard"), ("Big", "大", "easy"), ("Small", "小", "easy")],
        "listening": {
            "title": "Sale announcement",
            "source_type": "sentences",
            "ja": "本日はセール中です。全品三十パーセントオフです。三階の売り場へどうぞ。",
            "vi": "Hôm nay đang giảm giá. Tất cả sản phẩm giảm 30%. Mời quý khách lên quầy tầng 3.",
            "questions": [
                ("How big is the discount?", ["10%", "20%", "30%", "50%"], 2),
                ("Which floor?", ["1st", "2nd", "3rd", "4th"], 2),
            ],
        },
    },
    {
        "course": ("JLPT N5 Foundation", "N5"),
        "title": "Directions & Transport",
        "content": "Ask for directions and use public transport.",
        "vocab": [
            ("駅", "えき", "eki", "station", "駅はどこですか。", "Where is the station?"),
            ("右", "みぎ", "migi", "right", "右に曲がってください。", "Please turn right."),
            ("左", "ひだり", "hidari", "left", "左にあります。", "It's on the left."),
            ("まっすぐ", "まっすぐ", "massugu", "straight ahead", "まっすぐ行ってください。", "Please go straight."),
            ("電車", "でんしゃ", "densha", "train", "電車で行きます。", "I'll go by train."),
            ("近い", "ちかい", "chikai", "near", "駅は近いです。", "The station is close."),
        ],
        "reading": {
            "title": "道案内",
            "ja": "駅を出て、まっすぐ行ってください。二つ目の信号を右に曲がると、左に郵便局があります。図書館は郵便局のとなりです。",
            "vi": "Ra khỏi ga, hãy đi thẳng. Rẽ phải ở đèn giao thông thứ hai, bưu điện ở bên trái. Thư viện ở cạnh bưu điện.",
            "questions": [
                ("何番目の信号を曲がりますか。", ["一つ目", "二つ目", "三つ目", "四つ目"], 1),
                ("図書館はどこですか。", ["駅の前", "郵便局のとなり", "信号の右", "学校の後ろ"], 1),
            ],
        },
        "dialogue": {
            "title": "Lost in the city",
            "description": "Ask a passer-by how to get to the station.",
            "exchanges": [
                ("You", "すみません、駅はどこですか。", "Sumimasen, eki wa doko desu ka.", "Excuse me, where is the station?"),
                ("Passer-by", "この道をまっすぐ行って、左です。", "Kono michi o massugu itte, hidari desu.", "Go straight down this road, it's on the left."),
                ("You", "歩いて何分ぐらいですか。", "Aruite nanpun gurai desu ka.", "About how many minutes on foot?"),
                ("Passer-by", "五分ぐらいです。", "Gofun gurai desu.", "About five minutes."),
                ("You", "ありがとうございました。", "Arigatou gozaimashita.", "Thank you very much."),
            ],
        },
        "kanji": [("Right", "右", "medium"), ("Left", "左", "medium"), ("Station", "駅", "hard")],
        "listening": {
            "title": "Bus stop",
            "source_type": "dialogue",
            "ja": "A: このバスは空港に行きますか。\nB: いいえ、空港行きは五番のバスです。\nA: ありがとうございます。",
            "vi": "A: Xe buýt này có đi sân bay không?\nB: Không, xe đi sân bay là xe số 5.\nA: Cảm ơn.",
            "questions": [("Which bus goes to the airport?", ["No. 1", "No. 3", "No. 5", "No. 7"], 2)],
        },
    },
    {
        "course": ("JLPT N4 Business Japanese", "N4"),
        "title": "Business Etiquette",
        "content": "Polite expressions for the office and meetings.",
        "vocab": [
            ("会議", "かいぎ", "kaigi", "meeting", "三時から会議があります。", "There's a meeting from three."),
            ("資料", "しりょう", "shiryou", "documents / materials", "資料を準備しました。", "I prepared the materials."),
            ("名刺", "めいし", "meishi", "business card", "名刺をどうぞ。", "Here is my business card."),
            ("お疲れ様", "おつかれさま", "otsukaresama", "thanks for your hard work", "お疲れ様でした。", "Good work today."),
            ("担当", "たんとう", "tantou", "person in charge", "担当の鈴木です。", "I'm Suzuki, the person in charge."),
            ("確認", "かくにん", "kakunin", "confirmation", "確認いたします。", "I will confirm."),
        ],
        "reading": {
            "title": "会議のお知らせ",
            "ja": "来週の月曜日、午前十時から新しいプロジェクトの会議を行います。参加者は資料を読んでおいてください。場所は五階の会議室です。",
            "vi": "Thứ Hai tuần sau, từ 10 giờ sáng sẽ có cuộc họp về dự án mới. Người tham gia vui lòng đọc tài liệu trước. Địa điểm là phòng họp tầng 5.",
            "questions": [
                ("会議はいつですか。", ["今週の月曜日", "来週の月曜日", "来週の金曜日", "明日"], 1),
                ("会議の前に何をしますか。", ["名刺を作る", "資料を読む", "部屋を予約する", "電話をする"], 1),
                ("会議室は何階ですか。", ["三階", "四階", "五階", "六階"], 2),
            ],
        },
        "dialogue": {
            "title": "Exchanging business cards",
            "description": "Meet a client for the first time.",
            "exchanges": [
                ("Client", "はじめまして。ABC商事の佐藤と申します。", "Hajimemashite. ABC Shouji no Satou to moushimasu.", "Nice to meet you. My name is Sato, from ABC Trading."),
                ("You", "はじめまして。モジョの山田と申します。", "Hajimemashite. Mojo no Yamada to moushimasu.", "Nice to meet you. I'm Yamada from Mojo."),
                ("Client", "名刺をどうぞ。", "Meishi o douzo.", "Here's my card."),
                ("You", "ちょうだいいたします。", "Choudai itashimasu.", "Thank you, I'll gladly accept it."),
                ("Client", "本日はよろしくお願いいたします。", "Honjitsu wa yoroshiku onegai itashimasu.", "I look forward to working with you today."),
            ],
        },
        "kanji": [("Meeting", "会", "medium"), ("Company", "社", "medium"), ("Work", "仕", "hard")],
        "listening": {
            "title": "Voicemail from a client",
            "source_type": "sentences",
            "ja": "お世話になっております。ABC商事の佐藤です。明日の打ち合わせですが、午後二時に変更していただけますか。よろしくお願いいたします。",
            "vi": "Cảm ơn sự giúp đỡ của anh/chị. Tôi là Sato từ ABC Trading. Về cuộc họp ngày mai, có thể đổi sang 2 giờ chiều được không?",
            "questions": [
                ("What does the caller want?", ["Cancel the meeting", "Change the time", "Change the place", "Send documents"], 1),
                ("What is the new time?", ["10 AM", "Noon", "2 PM", "4 PM"], 2),
            ],
        },
    },
]

USERS = [
    # Onboarded learner with a week of history: shows the dashboard, streak, XP chart and due reviews.
    {
        "username": "demo",
        "email": "demo@mojo.io",
        "full_name": "Demo Learner",
        "password": "password123",
        "onboarded": True,
        "level": "N5",
        "xp": 1240,
        "streak": 7,
        "gems": 85,
    },
    # Fresh account for walking through onboarding live.
    {
        "username": "newbie",
        "email": "new@mojo.io",
        "full_name": "New Learner",
        "password": "password123",
        "onboarded": False,
        "level": None,
        "xp": 0,
        "streak": 0,
        "gems": 0,
    },
]

CONTENT_TABLES = [
    "activity_log",
    "vocabulary_review",
    "reading_attempt_answer",
    "reading_attempt",
    "listening_attempt",
    "dialogue_attempt",
    "kanji_practice_attempt",
    "reading_question_option",
    "reading_question",
    "reading_passage",
    "listening_question_option",
    "listening_question",
    "listening_practice",
    "dialogue_exchange",
    "dialogue",
    "kanji_practice",
    "vocabulary",
    "lesson",
    "course",
    "learner_profile",
    "auth_session",
    '"user"',
    "proficiency_level",
]


def _options(model, question, options: list[str], correct: int) -> None:
    for idx, option in enumerate(options):
        question.options.append(model(option_text=option, is_correct=idx == correct))


async def seed(reset: bool) -> None:
    async with SessionLocal() as db:
        if reset:
            await db.execute(text(f"TRUNCATE {', '.join(CONTENT_TABLES)} RESTART IDENTITY CASCADE"))
        elif await db.scalar(select(ProficiencyLevel.id).limit(1)) is not None:
            sys.exit("Database already has data. Use `make seed-reset` to wipe and reseed.")

        levels = {name: ProficiencyLevel(name=name, sort_order=i) for i, name in enumerate(LEVELS, start=1)}
        db.add_all(levels.values())

        courses: dict[str, Course] = {}
        lessons: list[Lesson] = []
        vocabulary: list[Vocabulary] = []
        for data in LESSONS:
            course_title, level_name = data["course"]
            if course_title not in courses:
                courses[course_title] = Course(
                    title=course_title, status="active", level=levels[level_name], sort_order=len(courses) + 1
                )
            course = courses[course_title]
            lesson = Lesson(
                course=course,
                title=data["title"],
                content=data["content"],
                difficulty=level_name,
                estimated_minutes=15,
                status="active",
                sort_order=sum(1 for le in lessons if le.course is course) + 1,
            )
            lessons.append(lesson)
            db.add(lesson)

            for kanji, kana, romaji, meaning, example, translation in data["vocab"]:
                word = Vocabulary(
                    lesson=lesson,
                    kanji=kanji,
                    kana=kana,
                    romaji=romaji,
                    meaning=meaning,
                    example_sentence=example,
                    example_translation=translation,
                )
                vocabulary.append(word)
                db.add(word)

            reading = data["reading"]
            passage = ReadingPassage(
                lesson=lesson, title=reading["title"], content_japanese=reading["ja"], content_vietnamese=reading["vi"]
            )
            for order, (question_text, options, correct) in enumerate(reading["questions"], start=1):
                question = ReadingQuestion(question_text=question_text, sort_order=order)
                _options(ReadingQuestionOption, question, options, correct)
                passage.questions.append(question)
            db.add(passage)

            dialogue_data = data["dialogue"]
            dialogue = Dialogue(lesson=lesson, title=dialogue_data["title"], description=dialogue_data["description"])
            for order, (speaker, ja, romaji, en) in enumerate(dialogue_data["exchanges"], start=1):
                dialogue.exchanges.append(
                    DialogueExchange(order_index=order, speaker=speaker, ja_text=ja, ja_romaji=romaji, en_text=en)
                )
            db.add(dialogue)

            for title, kanji, difficulty in data["kanji"]:
                db.add(KanjiPractice(lesson=lesson, title=title, kanji=kanji, difficulty=difficulty))

            listening = data["listening"]
            practice = ListeningPractice(
                lesson=lesson,
                title=listening["title"],
                source_type=listening["source_type"],
                transcript_japanese=listening["ja"],
                transcript_vietnamese=listening["vi"],
            )
            for order, (question_text, options, correct) in enumerate(listening["questions"], start=1):
                question = ListeningQuestion(question_text=question_text, sort_order=order)
                _options(ListeningQuestionOption, question, options, correct)
                practice.questions.append(question)
            db.add(practice)

        today = date.today()
        now = datetime.now(UTC)
        users: dict[str, User] = {}
        for data in USERS:
            user = User(
                username=data["username"],
                email=data["email"],
                full_name=data["full_name"],
                hashed_password=get_password_hash(data["password"]),
                is_onboarded=data["onboarded"],
                current_level=levels[data["level"]] if data["level"] else None,
                xp=data["xp"],
                streak=data["streak"],
                gems=data["gems"],
                last_activity_date=today if data["streak"] else None,
            )
            if data["onboarded"]:
                user.profile = LearnerProfile(target_level="N4", study_intention="travel", daily_study_minutes=15)
            users[data["username"]] = user
            db.add(user)
        await db.flush()

        # A week of activity for the demo learner, spread across skills, so charts aren't empty.
        demo = users["demo"]
        rng = random.Random(42)
        skills = list(await db.scalars(select(Skill)))
        for days_ago in range(7):
            day = now - timedelta(days=days_ago, hours=rng.randint(0, 6))
            for skill in rng.sample(skills, k=rng.randint(2, 4)):
                db.add(ActivityLog(user=demo, skill=skill, xp_earned=rng.choice([5, 10, 15, 20]), created_at=day))

        # SRS state for the first two lessons' words: some due now, some later, so review has cards.
        for idx, word in enumerate(vocabulary[:16]):
            due = now - timedelta(hours=1) if idx % 2 == 0 else now + timedelta(days=idx)
            db.add(
                VocabularyReview(
                    user=demo,
                    vocabulary=word,
                    ease_factor=2.5,
                    interval_days=idx % 5,
                    repetitions=1 + idx % 3,
                    next_review_at=due,
                    last_reviewed_at=now - timedelta(days=1 + idx % 3),
                    last_result="good",
                )
            )

        await db.commit()
        print(
            f"Seeded {len(levels)} levels, {len(courses)} courses, {len(lessons)} lessons, "
            f"{len(vocabulary)} words, {len(users)} users."
        )
        for data in USERS:
            print(f"  login: {data['email']} / {data['password']}")


if __name__ == "__main__":
    asyncio.run(seed(reset="--reset" in sys.argv))
