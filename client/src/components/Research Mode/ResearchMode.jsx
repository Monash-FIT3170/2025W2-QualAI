import React, { useState,useEffect,useRef  } from 'react';

import Landing from './steps/Landing';
import Codes from './steps/Codes';
import Themes from './steps/Themes';

import { API_ENDPOINTS } from "../../config/api";
import { useProject } from '../../contexts/ProjectContext';

export default function ResearchMode() {
  const [phase, setPhase] = useState("Landing");
  const [researchQuestion, setResearchQuestion] = useState("");
  const [codes, setCodes] = useState({});

  return (
    <div className="bg-slate-800 rounded-xl shadow-sm p-4 h-full flex flex-col">
      {phase === "Landing" && 
        <Landing 
          onNext={() => setPhase("Codes")}
          setResearchQuestion={setResearchQuestion}
       />
       }

      {phase === "Codes" &&
        <Codes 
          codes={codes}
          researchQuestion={researchQuestion}
          setCodes={setCodes}
          setPhase={setPhase}
          onNext = {() => setPhase("Themes")}
        />
      }

      {phase === "Themes" && 
        <Themes 
          codes = {codes}
          
        /> }
    </div>
  );
}
