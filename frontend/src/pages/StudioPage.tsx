// ============================================================================
// STUDIO PAGE - PURE LOGIC COMPONENT
// ============================================================================
// This file contains ONLY the business logic and state management.
// All styling is in src/styles/StudioPage.module.css
// ============================================================================

"use client";

import { useState } from "react";
import { toast } from "sonner";
import styles from "@/src/styles/StudioPage.module.css";
import { Upload, Video, ArrowRight, MonitorPlay, X, Plus, Sparkles } from "lucide-react";

export default function StudioPage() {
    // ==================== STATE ====================
    const [refFile, setRefFile] = useState<File | null>(null);
    const [materialFiles, setMaterialFiles] = useState<File[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [statusMsg, setStatusMsg] = useState("");

    // ==================== HANDLERS ====================
    const handleRefUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            setRefFile(e.target.files[0]);
            toast.success("Structural Reference Acquired");
        }
    };

    const handleMaterialUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setMaterialFiles(Array.from(e.target.files));
            toast.success(`${e.target.files.length} Neural Assets Staged`);
        }
    };

    const removeMaterial = (index: number) => {
        setMaterialFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const startMimic = async () => {
        if (!refFile || materialFiles.length === 0) {
            toast.error("Input missing: Reference & Material Required");
            return;
        }

        setIsGenerating(true);
        setStatusMsg("Initializing Neural Sequence...");
        setProgress(10);

        try {
            const formData = new FormData();
            formData.append("reference", refFile);
            materialFiles.forEach((file) => formData.append("clips", file));

            const uploadRes = await fetch("http://localhost:8000/api/upload", {
                method: "POST",
                body: formData,
            });
            const uploadData = await uploadRes.json();
            const sid = uploadData.session_id;

            await fetch(`http://localhost:8000/api/generate/${sid}`, { method: "POST" });

            const ws = new WebSocket(`ws://localhost:8000/ws/progress/${sid}`);

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setProgress(data.progress * 100);
                setStatusMsg(data.message);

                if (data.status === "complete") {
                    toast.success("Synthesis Complete");
                    setIsGenerating(false);
                    setProgress(0);
                    setStatusMsg("");
                } else if (data.status === "error") {
                    toast.error(`Neural Link Failure: ${data.message}`);
                    setIsGenerating(false);
                }
            };
        } catch (err) {
            toast.error("Critical System Interference");
            setIsGenerating(false);
        }
    };

    // ==================== RENDER ====================
    return (
        <div className={styles.pageContainer}>
            <div className={styles.contentWrapper}>
                {/* Hero Section */}
                <div className={styles.heroSection}>
                    <div className={styles.heroContent}>
                        <div className={styles.badge}>
                            <Sparkles className={styles.badgeIcon} />
                            <span className={styles.badgeText}>Synthesis Studio v3.4</span>
                        </div>
                        <h1 className={styles.heroTitle}>
                            Create. <span className={styles.heroTitleMuted}>Mimic.</span>
                            <br />
                            <span className={styles.heroTitleShiny}>Transcend.</span>
                        </h1>
                        <p className={styles.heroDescription}>
                            Replicate structural intent and cinematic pacing through neural reconstruction.
                        </p>
                    </div>

                    <button
                        onClick={startMimic}
                        disabled={isGenerating || !refFile || materialFiles.length === 0}
                        className={styles.primaryButton}
                    >
                        <div className={styles.buttonContent}>
                            <span className={styles.buttonText}>Initialize Sequence</span>
                            <ArrowRight className={styles.buttonIcon} />
                        </div>
                    </button>
                </div>

                {/* Pipeline Stack */}
                <div className={styles.pipelineStack}>
                    {/* Module 01: Blueprint */}
                    <div className={`${styles.module} ${refFile ? styles.moduleActive : ""}`}>
                        <div className={styles.moduleLayout}>
                            <div className={styles.moduleSidebar}>
                                <div className={styles.moduleIcon}>
                                    <Video className={styles.iconSvg} />
                                </div>
                                <div className={styles.moduleInfo}>
                                    <h3 className={styles.moduleTitle}>01. Structural Blueprint</h3>
                                    <p className={styles.moduleDescription}>
                                        Defines the conductory rhythm and motion intent.
                                    </p>
                                </div>
                            </div>

                            <div className={styles.moduleContent}>
                                {refFile ? (
                                    <div className={styles.uploadedFile}>
                                        <video
                                            src={URL.createObjectURL(refFile)}
                                            className={styles.uploadedVideo}
                                        />
                                        <div className={styles.uploadedOverlay}>
                                            <button onClick={() => setRefFile(null)} className={styles.removeButton}>
                                                <X className={styles.removeIcon} />
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className={styles.dropZone}>
                                        <input
                                            type="file"
                                            onChange={handleRefUpload}
                                            accept="video/*"
                                            className={styles.fileInput}
                                        />
                                        <Plus className={styles.dropZoneIcon} />
                                        <h4 className={styles.dropZoneText}>Target Reference</h4>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Module 02: Neural Seeds */}
                    <div className={`${styles.module} ${materialFiles.length > 0 ? styles.moduleActiveCyan : ""}`}>
                        <div className={styles.moduleLayout}>
                            <div className={styles.moduleSidebar}>
                                <div className={styles.moduleIconCyan}>
                                    <MonitorPlay className={styles.iconSvg} />
                                </div>
                                <div className={styles.moduleInfo}>
                                    <h3 className={styles.moduleTitle}>02. Neural Seeds</h3>
                                    <p className={styles.moduleDescription}>
                                        Source assets for the reconstruction matrix.
                                    </p>
                                    {materialFiles.length > 0 && (
                                        <span className={styles.assetCount}>{materialFiles.length} Assets Staged</span>
                                    )}
                                </div>
                            </div>

                            <div className={styles.moduleContentGrid}>
                                {materialFiles.length > 0 ? (
                                    <div className={styles.assetGrid}>
                                        {materialFiles.map((file, i) => (
                                            <div key={i} className={styles.assetCard}>
                                                <video
                                                    src={URL.createObjectURL(file)}
                                                    className={styles.assetVideo}
                                                />
                                                <button
                                                    onClick={() => removeMaterial(i)}
                                                    className={styles.assetRemove}
                                                >
                                                    <X className={styles.assetRemoveIcon} />
                                                </button>
                                            </div>
                                        ))}
                                        <div className={styles.assetAddCard}>
                                            <input
                                                type="file"
                                                onChange={handleMaterialUpload}
                                                multiple
                                                accept="video/*"
                                                className={styles.fileInput}
                                            />
                                            <Plus className={styles.assetAddIcon} />
                                        </div>
                                    </div>
                                ) : (
                                    <div className={styles.dropZoneLarge}>
                                        <input
                                            type="file"
                                            onChange={handleMaterialUpload}
                                            multiple
                                            accept="video/*"
                                            className={styles.fileInput}
                                        />
                                        <Plus className={styles.dropZoneIconLarge} />
                                        <h4 className={styles.dropZoneTextLarge}>Stage Source Clips</h4>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Progress Matrix */}
                <div className={`${styles.progressContainer} ${isGenerating ? styles.progressVisible : ""}`}>
                    <div className={styles.progressCard}>
                        <div className={styles.progressHeader}>
                            <div className={styles.progressInfo}>
                                <div className={styles.progressStatus}>
                                    <div className={styles.progressPulse} />
                                    <span className={styles.progressMessage}>{statusMsg}</span>
                                </div>
                            </div>
                            <div className={styles.progressPercent}>{Math.round(progress)}%</div>
                        </div>
                        <div className={styles.progressBarContainer}>
                            <div
                                className={styles.progressBar}
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
