export default function Codes({ codes, setCodes, setPhase }) {
  return (
    <div className="text-white">
      <button
        onClick={() => setPhase("Landing")}
        className=" text-slate-500 rounded hover:text-white text-xl font-bold"
      >
        {"<"}
      </button>
      <h2 className="text-xl font-semibold mb-4">Codes</h2>
      <p>generating codes...</p>
    </div>
  );
}