function ThemesToolBar({setPhase}) {
  return (
    <div className="text-white">
      <div className="relative mb-2 flex items-center justify-center">
        <button
          onClick={() => setPhase("Codes")}
          className="absolute left-0 text-slate-500 rounded hover:text-white text-xl font-bold"
        >
          {"<"}
        </button>
        <h2 className="text-xl font-semibold mb-1 text-center">Themes</h2>
      </div>
    </div>
  );
}

export default function Themes({ setPhase, codes} ) {
  return (
    <div>
      <ThemesToolBar
        setPhase={setPhase}
        codes={codes}
      />
    </div>
  );
}