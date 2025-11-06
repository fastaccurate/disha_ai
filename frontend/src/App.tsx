import "./App.css";
import { Routes, Route } from "react-router-dom";

import AssessmentsResults from "./pages/AssessmentsResults";
import AssessmentHome from "./pages/AssessmentHome";

import Assessment from "./pages/Assessment";

import { ROUTES } from "./configs/routes";

function App() {
  return (
    <div className="flex flex-col w-full h-full items-center min-h-screen bg-blue-50">
      <Routes>
        <Route path={ROUTES.HOME} element={<AssessmentHome />} />

        <Route path={ROUTES.START} element={<Assessment />} />

        <Route path={ROUTES.RESULTS} element={<AssessmentsResults />} />
      </Routes>
    </div>
  );
}

export default App;
