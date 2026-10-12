"use client";

import { useEffect, useState } from "react";
import { api, ApplicationRecord, ValidationResult } from "@/lib/api";
import { Card, Field, inputClass } from "./Shell";
import { StatusBadge } from "./StatusBadge";

export function ApplicationConfig({
  selectedId,
  onSelect,
  onReady,
}: {
  selectedId?: string;
  onSelect?: (application: ApplicationRecord) => void;
  onReady?: (application: ApplicationRecord, jewelry: string[], username: string, password: string) => void;
}) {
  const [items, setItems] = useState<ApplicationRecord[]>([]);
  const [name, setName] = useState("AIJewel Amplify");
  const [url, setUrl] = useState("https://demo-main.d1ug6v4fe77d43.amplifyapp.com/try-on");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [savedVideo, setSavedVideo] = useState(false);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setItems(await api.applications());
  }

  useEffect(() => {
    refresh().catch((exc: Error) => setError(exc.message));
  }, []);

  function choose(item: ApplicationRecord) {
    setName(item.name);
    setUrl(item.url || "");
    setUsername(item.username || "");
    setSavedVideo(Boolean(item.video_path));
    setValidation(null);
    onSelect?.(item);
  }

  async function onValidate() {
    if (!url.trim() || !username.trim() || !password) {
      setError("Enter the try-on link, username, and password.");
      return;
    }
    if (!faceFile && !savedVideo) {
      setError("Upload a video of the girl wearing no earrings.");
      return;
    }
    setBusy(true);
    setError("");
    setValidation(null);
    try {
      let record: ApplicationRecord;
      if (selectedId) {
        record = await api.updateApplication(selectedId, { url: url.trim(), username: username.trim() });
      } else {
        record = await api.createApplication({
          name: name.trim() || "AIJewel Amplify",
          type: "web",
          url: url.trim(),
          username: username.trim(),
        });
      }
      if (faceFile) {
        record = await api.uploadFaceVideo(record.id, faceFile);
        setSavedVideo(true);
      }
      onSelect?.(record);
      await refresh();
      const result = await api.validateApplication({
        url: url.trim(),
        username: username.trim(),
        password,
        type: "web",
        application_id: record.id,
      });
      setValidation(result);
      if (result.status === "success") {
        onReady?.(record, result.jewelry || [], username.trim(), password);
      }
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Validation failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
      <Card title="Try-on application">
        <div className="space-y-3">
          <Field label="Name">
            <input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} required />
          </Field>
          <Field label="Try-on link">
            <input
              className={inputClass}
              placeholder="https://xxxxx.amplifyapp.com/try-on"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
          </Field>
          <Field label="Username">
            <input className={inputClass} value={username} onChange={(event) => setUsername(event.target.value)} />
          </Field>
          <Field label="Password">
            <input
              className={inputClass}
              type="password"
              value={password}
              autoComplete="off"
              onChange={(event) => setPassword(event.target.value)}
            />
          </Field>
          <Field label="Face video, no earrings">
            <input
              className={inputClass}
              type="file"
              accept="video/mp4,video/webm,video/quicktime,.mp4,.webm,.mov"
              onChange={(event) => {
                setFaceFile(event.target.files?.[0] || null);
                setError("");
              }}
            />
            <p className="mt-1 text-xs text-zinc-500">
              {savedVideo
                ? "A face video is already saved. Choose a new file only if you want to replace it."
                : "This video is the camera. The chosen earring is placed on this girl."}
            </p>
          </Field>
          <button
            type="button"
            disabled={busy}
            onClick={onValidate}
            className="rounded bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950 disabled:opacity-50"
          >
            {busy ? "Validating try-on…" : "Validate Application"}
          </button>
          <p className="text-xs text-zinc-500">The password is used for this validation and the placement test. It is not saved.</p>
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          {validation ? (
            <div className="space-y-1 text-sm">
              <StatusBadge status={validation.status === "success" ? "PASS" : "FAIL"} />
              <p className={validation.reachable ? "text-emerald-400" : "text-red-400"}>
                {validation.reachable ? "✓" : "✗"} Application reachable
              </p>
              <p className={validation.login_successful ? "text-emerald-400" : "text-red-400"}>
                {validation.login_successful ? "✓" : "✗"} Login successful
              </p>
              <p className={validation.application_loaded ? "text-emerald-400" : "text-red-400"}>
                {validation.application_loaded ? "✓" : "✗"} Try-on application loaded
              </p>
              <p className="text-zinc-400">{validation.message}</p>
              {validation.screenshot_url ? (
                <img src={api.asset(validation.screenshot_url)} alt="Validation screenshot" className="mt-3 max-h-48 rounded border border-zinc-800" />
              ) : null}
            </div>
          ) : null}
        </div>
      </Card>
      <Card title="Saved applications">
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => choose(item)}
                className={`w-full rounded border px-3 py-2 text-left text-sm ${
                  selectedId === item.id ? "border-zinc-400" : "border-zinc-800"
                }`}
              >
                <span className="block text-zinc-100">{item.name}</span>
                <span className="text-xs text-zinc-500">
                  {item.id}
                  {item.video_path ? " · face video saved" : ""}
                </span>
              </button>
            </li>
          ))}
          {!items.length ? <li className="text-sm text-zinc-500">No applications saved.</li> : null}
        </ul>
      </Card>
    </div>
  );
}
