"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { motion } from "framer-motion";
import React, { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [format, setFormat] = useState("mp3");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [conversionProgress, setConversionProgress] = useState(0);
  const [downloadEta, setDownloadEta] = useState(0);
  const [conversionEta, setConversionEta] = useState(0);

  const handleDownload = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setDownloadProgress(0);
    setConversionProgress(0);
    setDownloadEta(0);
    setConversionEta(0);

    const formData = new FormData();
    formData.append("url", url);
    formData.append("format", format);

    try {
      const response = await fetch("http://localhost:8000/download", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = (await reader?.read()) ?? {
          done: true,
          value: undefined,
        };

        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6));

            if (data.type === "download") {
              setDownloadProgress(data.progress);
              setDownloadEta(data.eta);
            } else if (data.type === "conversion") {
              setConversionProgress(data.progress);
              setConversionEta(data.eta);
            } else if (data.type === "complete") {
              // Trigger file download
              const fileName = data.file_path;
              const downloadUrl = `http://localhost:8000/get-file/${encodeURIComponent(
                fileName
              )}`;
              const link = document.createElement("a");
              link.href = downloadUrl;
              link.download = fileName;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              setLoading(false);
            } else if (data.type === "error") {
              setError(data.message);
              setLoading(false);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("An unknown error occurred");
      }
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    if (seconds === 0) return "0s";
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes > 0 ? minutes + "m " : ""}${remainingSeconds}s`;
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        className="w-full max-w-md"
      >
        <Card className="p-8 rounded-lg shadow-2xl bg-white/10 border border-gray-700 backdrop-blur-md">
          <CardHeader className="text-center mb-6">
            <CardTitle className="text-5xl font-bold text-white">
              YouTube Downloader
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleDownload} className="space-y-6">
              <motion.div
                whileFocus={{ scale: 1.05 }}
                transition={{ duration: 0.3 }}
              >
                <Input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter YouTube URL"
                  className="w-full px-4 py-3 rounded-lg bg-white/20 placeholder-white/70 focus:bg-white/30 text-white"
                />
              </motion.div>
              <motion.div
                whileFocus={{ scale: 1.05 }}
                transition={{ duration: 0.3 }}
              >
                <Select value={format} onValueChange={setFormat}>
                  <SelectTrigger className="w-full rounded-lg bg-white/20 text-white">
                    <SelectValue placeholder="Select format" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mp3">MP3</SelectItem>
                    <SelectItem value="mp4">MP4</SelectItem>
                  </SelectContent>
                </Select>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }}>
                <Button
                  type="submit"
                  variant="outline"
                  className="w-full text-white font-bold py-3 px-4 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 transition-all duration-300 ease-in-out"
                  disabled={loading}
                >
                  {loading ? "Processing..." : "Download"}
                </Button>
              </motion.div>
            </form>
            {loading && (
              <div className="mt-6 space-y-4">
                <div>
                  <p className="text-white mb-2">
                    Downloading: {downloadProgress.toFixed(2)}%
                  </p>
                  <Progress value={downloadProgress} className="w-full" />
                  <p className="text-sm text-white mt-1">
                    Estimated time: {formatTime(downloadEta)}
                  </p>
                </div>
                <div>
                  <p className="text-white mb-2">
                    Converting: {conversionProgress.toFixed(2)}%
                  </p>
                  <Progress value={conversionProgress} className="w-full" />
                  <p className="text-sm text-white mt-1">
                    Estimated time: {formatTime(conversionEta)}
                  </p>
                </div>
              </div>
            )}
            {error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <Alert variant="destructive" className="mt-6">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
