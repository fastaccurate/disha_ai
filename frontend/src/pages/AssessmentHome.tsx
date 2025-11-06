import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import EvalAPI from "@/apis/EvalAPI";
import { AssessmentCard } from "@/components/AssessmentCard";
import { LoadingSpinner } from "@/components/ui/loadingspinner";
import { getAssessmentStartRoute } from "@/configs/routes";

interface Assessment {
  assessment_generation_id: number;

  instructions: {
    content: string;
    list: string[];
  };
  name: string;
}

const AssessmentHome = () => {
  const navigate = useNavigate();

  const [configs, setConfigs] = useState<Assessment[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchAssessmentConfigs = async () => {
      try {
        const data = await EvalAPI.getAssessmentConfigs();
        if (!data) return;
        setConfigs(data);
      } catch (error) {
        console.error("Failed to fetch assessment configs:", error);
      }
    };

    fetchAssessmentConfigs();
  }, []);

  const handleStartAssessment = async (data: any) => {
    if (!data) return;
    setIsLoading(true);
    try {
      const resp = await EvalAPI.startAssessment(data.assessment_generation_id);

      if (resp && resp.assessment_id) {
        const firstQuestionId = resp.questions[0].questions[0];
        navigate(getAssessmentStartRoute(resp.assessment_id, firstQuestionId));
      }
    } catch (error) {
      console.error("Failed to start assessment:", error);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-screen w-full p-4">
      {/* Content */}
      <div className="flex flex-col h-full min-h-screen w-full p-4">
        <h1 className="font-bold text-2xl text-black mb-4 ">Assessments</h1>

        <p className="font-medium text-[#8EA1B3] text-2xl">
          Select an assessment to start
        </p>

        {/* assessments card  */}
        <div className="flex flex-wrap gap-4 p-5">
          {configs.map((config, index) => (
            <AssessmentCard
              assessmentGenId={config.assessment_generation_id.toString()}
              key={index}
              assessmentName={config?.name}
              assessmentInstructions={config?.instructions?.list}
              assessmentNumber={index + 1}
              bgColor="#2059EE"
              startHandler={() => handleStartAssessment(config)}
            />
          ))}
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute top-0 left-0 w-full h-full bg-black/50 flex flex-col justify-center items-center z-100">
          <LoadingSpinner size={48} className="text-white" />
          <p className="text-4xl text-white">Starting Assessment...</p>
        </div>
      )}
    </div>
  );
};

export default AssessmentHome;
