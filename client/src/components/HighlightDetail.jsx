import { useEffect, useState, forwardRef, useImperativeHandle } from "react";
import HighlightItem from "./HighlightItem";

const HighlightDetail = forwardRef(({ projectId }, ref) => {
  const [highlightColors, setHighlightColors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!projectId) return;

    const fetchHighlights = async () => {
      try {
        const res = await fetch(`/projects/${projectId}/highlighters/`);
        if (!res.ok) return console.error("Failed to fetch:", res.statusText);

        const data = await res.json();
        setHighlightColors(
          data.map((h) => ({
            id: h.highlighter_id,
            label: h.label,
            color: h.colour,
            weight: Number(h.weight) || 1,
          }))
        );
      } catch (err) {
        console.error("Error fetching highlights:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHighlights();
  }, [projectId]);

  // Temporary message
  useEffect(() => {
    if (message) {
      const timeout = setTimeout(() => setMessage(""), 3000);
      return () => clearTimeout(timeout);
    }
  }, [message]);

  // Add new highlight 
  const handleAddColor = async () => {
    const newHighlight = { label: "New Highlight", color: "#000000", weight: 1 };

    try {
      const res = await fetch(`/projects/${projectId}/highlighters/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          label: newHighlight.label,
          colour: newHighlight.color,
          weight: String(newHighlight.weight),
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setHighlightColors((prev) => [
          ...prev,
          { ...newHighlight, id: data.highlighter_id },
        ]);
      }
    } catch (error) {
      console.error(error);
    }
  };

  // Local edits
  const handleColorChange = (id, field, value) => {
    setHighlightColors((prev) =>
      prev.map((h) => (h.id === id ? { ...h, [field]: value } : h))
    );
  };

  // Delete highlight locally 
  const handleRemoveColor = async (id) => {
    setHighlightColors((prev) => prev.filter((h) => h.id !== id));
    try {
      await fetch(`/projects/${projectId}/highlighters/${id}`, { method: "DELETE" });
    } catch (error) {
      console.error(error);
    }
  };

  // Saving highlights
  useImperativeHandle(ref, () => ({
    saveHighlights: async () => {
      try {
        for (const highlight of highlightColors) {
          if (highlight.id) {
            await fetch(`/projects/${projectId}/highlighters/${highlight.id}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                label: highlight.label,
                colour: highlight.color,
                weight: String(highlight.weight),
              }),
            });
          } else {
            await fetch(`/projects/${projectId}/highlighters/`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                label: highlight.label,
                colour: highlight.color,
                weight: String(highlight.weight),
              }),
            });
          }
        }

        setMessage("✨ All highlight changes saved! ✨");
      } catch (error) {
        console.error(error);
        setMessage("❌ Failed to save highlights.");
      }
    },
  }));

  if (loading) return <div className="text-gray-400">Loading highlights...</div>;

  const canRemove = highlightColors.length > 1;

  return (
    <div className="bg-slate-700 p-6 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-slate-200">Highlight Colors</h2>
        <button
          onClick={handleAddColor}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
        >
          <span className="mr-2 text-lg font-bold">+</span> Add Color
        </button>
      </div>

      <div className="space-y-3">
        {highlightColors.map((highlight) => (
          <HighlightItem
            key={highlight.id || highlight.label}
            highlight={highlight}
            onColorChange={handleColorChange}
            onRemove={handleRemoveColor}
            canRemove={canRemove}
          />
        ))}
      </div>

      {highlightColors.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No highlight colors configured. Add at least one to get started.
        </div>
      )}

      <div className="mt-6">
        {message && (
          <p className="text-sm text-center text-gray-300 mb-3 transition-opacity">
            {message}
          </p>
        )}
      </div>

    </div>
  );
});

export default HighlightDetail;
