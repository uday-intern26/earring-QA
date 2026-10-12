"use client";

import { ApplicationConfig } from "@/components/ApplicationConfig";

export default function ApplicationsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Applications</h2>
      <ApplicationConfig />
    </div>
  );
}
