import HighlightItem from "./HighlightItem";

const HighlightDetail = ({ highlightColors, onColorChange, onAddColor, onRemoveColor }) => {
  const canRemove = highlightColors.length > 1;

  return (
    <div className="bg-slate-700 p-6 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-200">Highlight Colors</h2>
        </div>
        <button
        onClick={onAddColor}
        className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
        >
        <span className="mr-2 text-lg font-bold">+</span>
        Add Color
        </button>

      </div>

      <div className="space-y-3">
        {highlightColors.map((highlight) => (
          <HighlightItem
            key={highlight.id}
            highlight={highlight}
            onColorChange={onColorChange}
            onRemove={onRemoveColor}
            canRemove={canRemove}
          />
        ))}
      </div>

      {highlightColors.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No highlight colors configured. Add at least one to get started.
        </div>
      )}
    </div>
  );
};

export default HighlightDetail;