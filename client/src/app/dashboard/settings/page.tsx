'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { getCurrentUser } from '@/lib/auth';

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getCurrentUser().then(setUser);
  }, []);

  if (!user) return <p className="text-muted-foreground animate-pulse">Loading settings...</p>;

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-3xl font-bold tracking-tighter text-primary">Settings</h2>
        <p className="text-muted-foreground">Manage your account settings and preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
          <CardDescription>Update your account details here.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Full Name</label>
            <Input defaultValue={user.full_name || user.username} readOnly className="bg-gray-50 text-gray-500" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Email Address</label>
            <Input defaultValue={user.email} readOnly className="bg-gray-50 text-gray-500" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Phone Number</label>
            <Input defaultValue={user.phone || ''} readOnly className="bg-gray-50 text-gray-500" />
          </div>
          <p className="text-xs text-muted-foreground italic">* To change your profile details, please contact support.</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-bold text-primary">Email Notifications</p>
              <p className="text-sm text-muted-foreground">Receive daily reminders to practice.</p>
            </div>
            <Button variant="outline" className="border-emerald-500 text-emerald-600 bg-emerald-50 pointer-events-none">Enabled</Button>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="font-bold text-primary">Public Profile</p>
              <p className="text-sm text-muted-foreground">Allow others to see your XP and streak.</p>
            </div>
            <Button variant="outline" className="pointer-events-none">Disabled</Button>
          </div>
        </CardContent>
      </Card>
      
      <div className="flex justify-end">
         <Button className="bg-primary hover:bg-primary/90">Save Changes</Button>
      </div>
    </div>
  );
}