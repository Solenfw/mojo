'use client';

import React from 'react';
import { BookOpen } from 'lucide-react';

export default function CurriculumPage() {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center p-12">
      <div className="w-24 h-24 bg-secondary rounded-full flex items-center justify-center mb-6">
        <BookOpen className="w-12 h-12 text-primary" />
      </div>
      <h2 className="text-3xl font-bold tracking-tighter text-primary mb-2">Curriculum Roadmap</h2>
      <p className="text-muted-foreground max-w-md">Your structured path to JLPT N5 mastery. We're organizing the next set of modules for you.</p>
    </div>
  );
}