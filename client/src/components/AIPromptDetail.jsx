const AIAdditionalDetail = ({ additionalInstructions, onInputChange }) => {
  return (
    <div className="bg-slate-700 p-6 rounded-lg">
      <h2 className="text-xl font-semibold text-slate-200 mb-2">Additional AI Instructions</h2>
      
      <textarea
        value={additionalInstructions}
        onChange={(e) => onInputChange('additionalInstructions', e.target.value)}
        rows={6}
        className="bg-slate-600 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
        placeholder="Enter additional instructions that will be appended to the base AI prompt..."
      />
      
    </div>
  );
};

export default AIAdditionalDetail;