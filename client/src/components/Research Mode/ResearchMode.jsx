import React, { useState,useEffect,useRef  } from 'react';

import Landing from './steps/Landing';
import Codes from './steps/Codes';
import Themes from './steps/Themes';

import { API_ENDPOINTS } from "../../config/api";
import { useProject } from '../../contexts/ProjectContext';

export default function ResearchMode({ phase, setPhase, researchQuestion, setResearchQuestion, codes, setCodes }) {
  const { activeProjectId } = useProject();
  

  useEffect(() => {
      const fetchCodes = async () => {
          try {
            const response = await fetch(API_ENDPOINTS.listProjectCodes(activeProjectId), {
            method: "GET", // explicitly specify GET (optional; default is GET)
            headers: {
              "Content-Type": "application/json", // optional for GET
            },
          });
  
            if (!response.ok) throw new Error("Failed to fetch codes");
      
            const data = await response.json();
            setCodes(data.codes || []); // expect [{ id, code, quotes }]
        } catch (error) {
          console.error(error);
        }
      };
  
      fetchCodes();
        
      }, [activeProjectId]);

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
          setResearchQuestion={setResearchQuestion}
          onNext = {() => setPhase("Themes")}
        />
      }

      {phase === "Themes" && 
        <Themes 
          codes = {codes}
          setPhase ={setPhase}
        /> }
    </div>
  );
}
