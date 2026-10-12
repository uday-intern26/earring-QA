"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, ApplicationRecord, TestRecord } from "@/lib/api";
import { Card, Field, inputClass } from "./Shell";

const EMPTY = {
  name: "Try-on URL earring on earlobe",
  jewelry_id: "Gold Diamond Bezel Stud Earring",
  jewelry_type: "earring",
  ear_side: "left",
  capture_fps: 5,
  capture_duration_seconds: 6,
  minimum_confidence: 0.5,
  pass_threshold: 0.1,
  fail_threshold: 0.15,
  minimum_pass_rate: 0.95,
  maximum_consecutive_failures: 2,
};

export function TestConfiguration({
  applicationId,
  onCreated,
}: {
  applicationId?: string;
  onCreated?: (test: TestRecord) => void;
}) {
  const [applications, setApplications] = useState<ApplicationRecord[]>([]);
  const [tests, setTests] = useState<TestRecord[]>([]);
  const [form, setForm] = useState(EMPTY);
  const [appId, setAppId] = useState(applicationId || "");
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.applications(), api.tests()])
      .then(([apps, existing]) => {
        if (cancelled) return;
        setApplications(apps);
        setTests(existing);
      })
      .catch((exc: Error) => {
        if (!cancelled) setError(exc.message);
      });
    return () => {
      cancelled = true;
    };
  }, [applicationId]);

  useEffect(() => setAppId(applicationId || ""), [applicationId]);

  function update(key: string, value: string) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const created = await api.createTest({
        ...form,
        application_id: appId,
        reference_id: null,
        jewelry_id: form.jewelry_id || null,
        capture_fps: Number(form.capture_fps),
        capture_duration_seconds: Number(form.capture_duration_seconds),
        minimum_confidence: Number(form.minimum_confidence),
        pass_threshold: Number(form.pass_threshold),
        fail_threshold: Number(form.fail_threshold),
        minimum_pass_rate: Number(form.minimum_pass_rate),
        maximum_consecutive_failures: Number(form.maximum_consecutive_failures),
      });
      setTests(await api.tests());
      onCreated?.(created);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Unable to create the test");
    }
  }

  return (
    <Card title="Test Configuration">
      <form className="grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
        <Field label="Test Name">
          <input className={inputClass} value={form.name} onChange={(event) => update("name", event.target.value)} required />
        </Field>
        <Field label="Application">
          <select className={inputClass} value={appId} onChange={(event) => setAppId(event.target.value)} required>
            <option value="">Select an application</option>
            {applications.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Jewellery ID">
          <input className={inputClass} placeholder="Gold Diamond Bezel Stud Earring" value={form.jewelry_id} onChange={(event) => update("jewelry_id", event.target.value)} />
        </Field>
        <Field label="Jewellery Type">
          <select className={inputClass} value={form.jewelry_type} onChange={(event) => update("jewelry_type", event.target.value)}>
            <option value="earring">Earring</option>
            <option value="necklace">Necklace</option>
            <option value="bracelet">Bracelet</option>
            <option value="ring">Ring</option>
            <option value="bangle">Bangle</option>
          </select>
        </Field>
        <Field label="Ear Side">
          <select className={inputClass} value={form.ear_side} onChange={(event) => update("ear_side", event.target.value)}>
            <option value="left">Left</option>
            <option value="right">Right</option>
            <option value="both">Both</option>
          </select>
        </Field>
        <Field label="Capture FPS">
          <select className={inputClass} value={form.capture_fps} onChange={(event) => update("capture_fps", event.target.value)}>
            {[1, 2, 5, 10].map((fps) => (
              <option key={fps} value={fps}>
                {fps}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Capture duration (seconds)">
          <input className={inputClass} type="number" value={form.capture_duration_seconds} onChange={(event) => update("capture_duration_seconds", event.target.value)} />
        </Field>
        <Field label="Minimum Landmark Confidence">
          <input className={inputClass} type="number" step="0.01" value={form.minimum_confidence} onChange={(event) => update("minimum_confidence", event.target.value)} />
        </Field>
        <Field label="Pass Threshold">
          <input className={inputClass} type="number" step="0.01" value={form.pass_threshold} onChange={(event) => update("pass_threshold", event.target.value)} />
        </Field>
        <Field label="Fail Threshold">
          <input className={inputClass} type="number" step="0.01" value={form.fail_threshold} onChange={(event) => update("fail_threshold", event.target.value)} />
        </Field>
        <Field label="Minimum Pass Rate">
          <input className={inputClass} type="number" step="0.01" value={form.minimum_pass_rate} onChange={(event) => update("minimum_pass_rate", event.target.value)} />
        </Field>
        <Field label="Maximum Consecutive Failures">
          <input className={inputClass} type="number" value={form.maximum_consecutive_failures} onChange={(event) => update("maximum_consecutive_failures", event.target.value)} />
        </Field>
        <div className="md:col-span-2">
          <button className="rounded bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950" type="submit">
            Save Test Configuration
          </button>
          {error ? <p className="mt-2 text-sm text-red-400">{error}</p> : null}
        </div>
      </form>
      <ul className="mt-4 space-y-2 text-sm text-zinc-400">
        {tests.map((test) => (
          <li key={test.id}>
            <button type="button" className="underline" onClick={() => onCreated?.(test)}>
              {test.id} · {test.name}
            </button>
          </li>
        ))}
      </ul>
    </Card>
  );
}
