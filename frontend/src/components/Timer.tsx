import { useEffect, useState } from "react";
import { parseISO } from "date-fns";
import { CalculationsUtil } from "../utils/calculations";
import { icons } from "../assets";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function Timer({
  assessmentId,
  submitSolution,
  ApiClass,
  navigationUrl,
}: {
  assessmentId: number;
  submitSolution: (navToReport: boolean) => void;
  ApiClass: any;
  navigationUrl: string;
}) {
  const [testDuration, setTestDuration] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [nowTime, setNowTime] = useState(Date.now());
  const [timeRemaining, setTimeRemaining] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);

  const navigate = useNavigate();

  useEffect(() => {
    if (!startTime || !testDuration) return;
    const endTime = startTime + testDuration * 1000;

    const remainingTimeInSeconds = Math.max(
      0,
      Math.floor((endTime - nowTime) / 1000)
    );

    const formattedTime = CalculationsUtil.formatTime(remainingTimeInSeconds);
    setTimeRemaining(formattedTime);
  }, [nowTime, startTime, testDuration]);

  useEffect(() => {
    if (!submitted && timeRemaining == "00:00") {
      submitSolution(false);
      setSubmitted(true);
    }
  }, [timeRemaining, submitted]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await ApiClass.getState(assessmentId.toString());
        const startTime = parseISO(data.start_time).getTime();
        setStartTime(startTime);
        setTestDuration(data.test_duration);
      } catch (error) {
        console.error(error);

        // if response status is 400, then set the test duration to mock value (30 minutes)
        if (error instanceof Error && (error as any).response?.status === 400) {
          setTestDuration(30 * 60);
          setStartTime(Date.now());
        }
      }
    };

    fetchData();
  }, [assessmentId]);

  useEffect(() => {
    const intervalID = setInterval(() => setNowTime(Date.now()), 1000);
    return () => clearInterval(intervalID);
  }, []);

  const navigateToReport = () => {
    navigate(`/${navigationUrl}=${assessmentId}`);
  };

  return (
    <div className="flex flex-row items-center gap-2 bg-[#2059EE] px-4 py-1 rounded-full text-white">
      <img
        src={icons.timeStart}
        alt="Clock"
        className="bg-white p-0.5 w-[24px] h-[24px] rounded-full"
      />
      <span>{timeRemaining}</span>

      {timeRemaining == "00:00" && (
        <div className="absolute inset-0 flex justify-center items-center bg-white/10 backdrop-blur-sm rounded-lg z-50 cursor-not-allowed">
          <div className="flex flex-col justify-center items-center bg-white rounded-lg shadow-md p-8">
            <img
              src={icons.timeOver}
              alt="Time Over"
              className="w-[200px] h-[200px] mb-5"
            />
            <h2 className="text-xl font-semibold mb-5 text-black">Time Over</h2>
            <Button
              variant="default"
              className="bg-[#2059EE] text-white rounded-lg"
              onClick={navigateToReport}
            >
              Check Report
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
