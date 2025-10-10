const HighlightItem = ({ highlight, onColorChange, onRemove, canRemove }) => {
  return (
    <div className="flex items-center gap-4 p-4 bg-slate-700 rounded-lg border border-gray-200">
      <div className="flex-shrink-0 relative">
        <input
          type="color"
          value={highlight.color}
          onChange={(e) => onColorChange(highlight.id, 'color', e.target.value)}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          id={`color-${highlight.id}`}
        />
        <label
          htmlFor={`color-${highlight.id}`}
          className="block w-9 h-9 rounded-full cursor-pointer border-2 border-transparent"
          style={{ backgroundColor: highlight.color }}
        />
      </div>

      <div className="flex-1 min-w-[100px]">
        <input
          type="text"
          value={highlight.label}
          onChange={(e) => onColorChange(highlight.id, 'label', e.target.value)}
          className="bg-slate-600 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Label"
        />
      </div>

      <div className="flex-shrink-0">
        <select
          value={highlight.weight}
          onChange={(e) => onColorChange(highlight.id, 'weight', parseInt(e.target.value))}
          className="bg-slate-800 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={1}>1 - Ignore</option>
          <option value={2}>2 - Low</option>
          <option value={3}>3 - Medium</option>
          <option value={4}>4 - High</option>
          <option value={5}>5 - Critical</option>
        </select>
      </div>

        <button
        onClick={() => onRemove(highlight.id)}
        className="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
        disabled={!canRemove}
        >
        <span className="font-bold">❌</span>
        </button>
    </div>
  );
};

export default HighlightItem;