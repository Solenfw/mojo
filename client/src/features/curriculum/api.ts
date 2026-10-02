/**
 * The curriculum tree (levels → courses → lessons) that every practice screen browses.
 * A lesson has no type of its own: screens filter on what it contains (vocabularyCount,
 * readingPassages, dialogues, kanjiPractices).
 */
import { api, unwrap } from '@/lib/api-client';
import type { CourseRead, LessonDetailRead, LessonRead, ProficiencyLevelRead } from '@/types/api.generated';

export const getLevels = async (): Promise<ProficiencyLevelRead[]> =>
  unwrap(await api.GET('/api/v1/levels'), 'Unable to load levels.').data;

export const getCourses = async (levelId?: number): Promise<CourseRead[]> =>
  unwrap(await api.GET('/api/v1/courses', { params: { query: { levelId } } }), 'Unable to load courses.').data;

export const getLessons = async (courseId: number): Promise<LessonRead[]> =>
  unwrap(
    await api.GET('/api/v1/courses/{course_id}/lessons', { params: { path: { course_id: courseId } } }),
    'Unable to load lessons.',
  ).data;

export const getLesson = async (lessonId: number): Promise<LessonDetailRead> =>
  unwrap(
    await api.GET('/api/v1/lessons/{lesson_id}', { params: { path: { lesson_id: lessonId } } }),
    'Unable to load the lesson.',
  ).data;

/**
 * Lessons of the first course at a level (by name, e.g. 'N5'), with what each one contains.
 * One request per lesson until the lesson list reports its contents (docs/api-layer.md, gap G1).
 */
export const getLevelLessons = async (levelName: string): Promise<LessonDetailRead[]> => {
  const level = (await getLevels()).find((item) => item.name === levelName);
  if (!level) return [];
  const [course] = await getCourses(level.id);
  if (!course) return [];
  const lessons = await getLessons(course.id);
  return Promise.all(lessons.map((lesson) => getLesson(lesson.id)));
};
