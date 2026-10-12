"use client";

import { TestConfiguration } from "@/components/TestConfiguration";

export default function TestsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Test Configurations</h2>
      <TestConfiguration />
    </div>
  );
}
