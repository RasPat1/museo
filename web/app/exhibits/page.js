"use client";

import { useEffect, useState, useCallback } from "react";

export default function ExhibitsPage() {
    const [exhibits, setExhibits] = useState([]);
    const [museums, setMuseums] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [filterMuseum, setFilterMuseum] = useState("all");
    const [filterStatus, setFilterStatus] = useState("all"); // all | interested | skipped | undecided
    const [curation, setCuration] = useState({}); // { exhibitId: "interested" | "skipped" }
    const [selectedExhibit, setSelectedExhibit] = useState(null);

    // Load curation state from localStorage
    useEffect(() => {
        try {
            const saved = localStorage.getItem("museo-curation");
            if (saved) setCuration(JSON.parse(saved));
        } catch { }
    }, []);

    // Save curation to localStorage
    const saveCuration = useCallback(
        (next) => {
            setCuration(next);
            localStorage.setItem("museo-curation", JSON.stringify(next));
        },
        []
    );

    // Load selected museums from localStorage then fetch exhibits
    useEffect(() => {
        const savedMuseums = localStorage.getItem("museo-selected-museums");
        const museumIds = savedMuseums ? JSON.parse(savedMuseums) : [];

        const params = new URLSearchParams();
        if (museumIds.length > 0) {
            params.set("museums", museumIds.join(","));
        }

        Promise.all([
            fetch(`/api/exhibits?${params}`).then((r) => r.json()),
            fetch("/api/museums").then((r) => r.json()),
        ])
            .then(([exhibitData, museumData]) => {
                setExhibits(exhibitData);
                setMuseums(museumData);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    const markInterested = (id) => {
        saveCuration({
            ...curation,
            [id]: curation[id] === "interested" ? undefined : "interested",
        });
    };

    const markSkipped = (id) => {
        saveCuration({
            ...curation,
            [id]: curation[id] === "skipped" ? undefined : "skipped",
        });
    };

    // Filter exhibits
    const filtered = exhibits.filter((ex) => {
        // Search
        if (
            search &&
            !ex.title.toLowerCase().includes(search.toLowerCase()) &&
            !(ex.description || "").toLowerCase().includes(search.toLowerCase())
        ) {
            return false;
        }
        // Museum filter
        if (filterMuseum !== "all" && ex.museum_id !== filterMuseum) {
            return false;
        }
        // Status filter
        if (filterStatus === "interested" && curation[ex.id] !== "interested")
            return false;
        if (filterStatus === "skipped" && curation[ex.id] !== "skipped")
            return false;
        if (filterStatus === "undecided" && curation[ex.id]) return false;
        return true;
    });

    const interestedCount = Object.values(curation).filter(
        (v) => v === "interested"
    ).length;

    // Build unique museum list from current exhibits
    const exhibitMuseums = [
        ...new Map(
            exhibits.map((e) => [e.museum_id, e.museum_name])
        ).entries(),
    ];

    return (
        <div className="container">
            <div className="page-header">
                <h1 className="page-header__title">Exhibits</h1>
                <p className="page-header__subtitle">
                    Browse, evaluate, and build your shortlist.
                    {interestedCount > 0 && (
                        <span style={{ color: "var(--c-success)", marginLeft: 8 }}>
                            {interestedCount} exhibit{interestedCount !== 1 ? "s" : ""}{" "}
                            shortlisted ✓
                        </span>
                    )}
                </p>
            </div>

            {/* Filters */}
            <div className="filter-bar">
                <input
                    className="search-input"
                    type="text"
                    placeholder="Search exhibits..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                <div className="filter-pills">
                    {[
                        { key: "all", label: "All" },
                        { key: "interested", label: `★ Interested (${interestedCount})` },
                        { key: "skipped", label: "Skipped" },
                        { key: "undecided", label: "Undecided" },
                    ].map((f) => (
                        <button
                            key={f.key}
                            className={`filter-pill ${filterStatus === f.key ? "active" : ""
                                }`}
                            onClick={() => setFilterStatus(f.key)}
                        >
                            {f.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Museum pills */}
            {exhibitMuseums.length > 1 && (
                <div className="filter-pills" style={{ marginBottom: "var(--space-xl)" }}>
                    <button
                        className={`filter-pill ${filterMuseum === "all" ? "active" : ""}`}
                        onClick={() => setFilterMuseum("all")}
                    >
                        All Museums
                    </button>
                    {exhibitMuseums.map(([id, name]) => (
                        <button
                            key={id}
                            className={`filter-pill ${filterMuseum === id ? "active" : ""}`}
                            onClick={() => setFilterMuseum(id)}
                        >
                            {name.length > 25 ? name.substring(0, 25) + "…" : name}
                        </button>
                    ))}
                </div>
            )}

            {/* Exhibit grid */}
            {loading ? (
                <div className="grid grid--exhibits">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="card">
                            <div className="skeleton" style={{ height: 200 }} />
                            <div className="card__body">
                                <div
                                    className="skeleton"
                                    style={{ height: 18, width: "80%", marginBottom: 8 }}
                                />
                                <div
                                    className="skeleton"
                                    style={{ height: 14, width: "50%", marginBottom: 12 }}
                                />
                                <div className="skeleton" style={{ height: 12, width: "60%" }} />
                            </div>
                        </div>
                    ))}
                </div>
            ) : filtered.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state__icon">🖼️</div>
                    <p className="empty-state__text">
                        {exhibits.length === 0
                            ? "No exhibits yet. Select museums first, then run the scraper."
                            : "No exhibits match your filters."}
                    </p>
                </div>
            ) : (
                <div className="grid grid--exhibits">
                    {filtered.map((ex) => (
                        <div key={ex.id} className="card">
                            {ex.image_url ? (
                                <img
                                    className="card__image"
                                    src={ex.image_url}
                                    alt={ex.title}
                                    loading="lazy"
                                    onError={(e) => {
                                        e.target.style.display = "none";
                                    }}
                                />
                            ) : (
                                <div
                                    className="card__image"
                                    style={{
                                        background:
                                            "linear-gradient(135deg, var(--c-surface-2), var(--c-border))",
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        fontSize: "2rem",
                                        color: "var(--c-text-dim)",
                                    }}
                                >
                                    🎨
                                </div>
                            )}
                            <div className="card__body">
                                <p className="card__subtitle">{ex.museum_name}</p>
                                <h3 className="card__title">{ex.title}</h3>
                                {(ex.start_date || ex.end_date) && (
                                    <p className="card__meta">
                                        {ex.start_date && ex.end_date
                                            ? `${ex.start_date} → ${ex.end_date}`
                                            : ex.start_date
                                                ? `From ${ex.start_date}`
                                                : `Until ${ex.end_date}`}
                                    </p>
                                )}

                                <div className="card__actions">
                                    <button
                                        className={`btn btn--interested btn--sm ${curation[ex.id] === "interested" ? "active" : ""
                                            }`}
                                        onClick={() => markInterested(ex.id)}
                                    >
                                        {curation[ex.id] === "interested"
                                            ? "★ Interested"
                                            : "☆ Interested"}
                                    </button>
                                    <button
                                        className={`btn btn--skip btn--sm ${curation[ex.id] === "skipped" ? "active" : ""
                                            }`}
                                        onClick={() => markSkipped(ex.id)}
                                    >
                                        Skip
                                    </button>
                                    <button
                                        className="btn btn--ghost btn--sm"
                                        onClick={() => setSelectedExhibit(ex)}
                                    >
                                        Details
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Detail modal */}
            {selectedExhibit && (
                <div
                    className="modal-overlay"
                    onClick={(e) => {
                        if (e.target === e.currentTarget) setSelectedExhibit(null);
                    }}
                >
                    <div className="modal" style={{ position: "relative" }}>
                        <button
                            className="modal__close"
                            onClick={() => setSelectedExhibit(null)}
                        >
                            ✕
                        </button>

                        {selectedExhibit.image_url && (
                            <img
                                className="modal__image"
                                src={selectedExhibit.image_url}
                                alt={selectedExhibit.title}
                                onError={(e) => {
                                    e.target.style.display = "none";
                                }}
                            />
                        )}

                        <div className="modal__body">
                            <h2 className="modal__title">{selectedExhibit.title}</h2>
                            <p className="modal__museum">{selectedExhibit.museum_name}</p>

                            {(selectedExhibit.start_date || selectedExhibit.end_date) && (
                                <p className="modal__dates">
                                    {selectedExhibit.start_date && selectedExhibit.end_date
                                        ? `${selectedExhibit.start_date} → ${selectedExhibit.end_date}`
                                        : selectedExhibit.start_date
                                            ? `From ${selectedExhibit.start_date}`
                                            : `Until ${selectedExhibit.end_date}`}
                                </p>
                            )}

                            {selectedExhibit.description && (
                                <p className="modal__description">
                                    {selectedExhibit.description}
                                </p>
                            )}

                            <div className="modal__actions">
                                <button
                                    className={`btn btn--interested ${curation[selectedExhibit.id] === "interested" ? "active" : ""
                                        }`}
                                    onClick={() => markInterested(selectedExhibit.id)}
                                >
                                    {curation[selectedExhibit.id] === "interested"
                                        ? "★ Interested"
                                        : "☆ Mark Interested"}
                                </button>
                                <button
                                    className={`btn btn--skip ${curation[selectedExhibit.id] === "skipped" ? "active" : ""
                                        }`}
                                    onClick={() => markSkipped(selectedExhibit.id)}
                                >
                                    Skip
                                </button>
                                {selectedExhibit.url && (
                                    <a
                                        href={selectedExhibit.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn--secondary"
                                    >
                                        Visit Museum Page →
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
