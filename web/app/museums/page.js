"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function MuseumsPage() {
    const [museums, setMuseums] = useState([]);
    const [selected, setSelected] = useState([]);
    const [loading, setLoading] = useState(true);

    // Load museums from API
    useEffect(() => {
        fetch("/api/museums")
            .then((r) => r.json())
            .then((data) => {
                setMuseums(data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    // Load saved selections from localStorage
    useEffect(() => {
        try {
            const saved = localStorage.getItem("museo-selected-museums");
            if (saved) setSelected(JSON.parse(saved));
        } catch { }
    }, []);

    // Save selections to localStorage
    useEffect(() => {
        if (selected.length > 0) {
            localStorage.setItem("museo-selected-museums", JSON.stringify(selected));
        }
    }, [selected]);

    const toggle = (id) => {
        setSelected((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    };

    const selectAll = () => setSelected(museums.map((m) => m.id));
    const clearAll = () => {
        setSelected([]);
        localStorage.removeItem("museo-selected-museums");
    };

    return (
        <div className="container">
            <div className="page-header">
                <h1 className="page-header__title">Museums</h1>
                <p className="page-header__subtitle">
                    Pick the museums you want to follow. Your selections filter the
                    exhibits you&rsquo;ll see.
                </p>
            </div>

            <div className="filter-bar">
                <span style={{ color: "var(--c-text-muted)", fontSize: "0.85rem" }}>
                    {selected.length} of {museums.length} selected
                </span>
                <button className="btn btn--ghost btn--sm" onClick={selectAll}>
                    Select All
                </button>
                <button className="btn btn--ghost btn--sm" onClick={clearAll}>
                    Clear
                </button>
                <span style={{ flex: 1 }} />
                <Link href="/exhibits" className="btn btn--primary">
                    Browse Exhibits →
                </Link>
            </div>

            {loading ? (
                <div className="grid grid--museums">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="card">
                            <div className="skeleton" style={{ height: 160 }} />
                            <div className="card__body">
                                <div
                                    className="skeleton"
                                    style={{ height: 20, width: "70%", marginBottom: 8 }}
                                />
                                <div className="skeleton" style={{ height: 14, width: "50%" }} />
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="grid grid--museums">
                    {museums.map((museum) => (
                        <div
                            key={museum.id}
                            className={`card museum-card ${selected.includes(museum.id) ? "selected" : ""
                                }`}
                            onClick={() => toggle(museum.id)}
                        >
                            <div
                                className="card__image"
                                style={{
                                    background: `linear-gradient(135deg, var(--c-surface-2), var(--c-border))`,
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    fontSize: "2.5rem",
                                }}
                            >
                                🏛️
                            </div>
                            <div className="museum-card__check">
                                {selected.includes(museum.id) ? "✓" : ""}
                            </div>
                            <div className="card__body">
                                <h3 className="card__title">{museum.name}</h3>
                                <p className="card__meta">{museum.address}</p>
                                {museum.url && (
                                    <a
                                        href={museum.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn--ghost btn--sm"
                                        onClick={(e) => e.stopPropagation()}
                                        style={{ marginTop: 8 }}
                                    >
                                        Visit Website →
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
