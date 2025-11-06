import { Button } from "@/components/ui/button";
import EvalAPI from "@/apis/EvalAPI";
import Timer from "@/components/Timer";

interface TopPanelProps {
  questionModal: () => void;
  confirmationModal: () => void;
  TimeUpHandler: any;
  assessmentId: string;
}

const TopPanel = (props: TopPanelProps) => {
  return (
    <div className="flex flex-row justify-end mb-2.5 w-full gap-2.5">
      <div className="flex flex-row gap-2.5">
        <Timer
          assessmentId={Number(props.assessmentId)}
          submitSolution={props.TimeUpHandler}
          ApiClass={EvalAPI}
          navigationUrl="/fetch-individual-scorecard?assessment_id?assessment_id"
        />
        <Button
          className="rounded-[10px] bg-[#2059EE] text-white hover:bg-[#2059EE]/90"
          onClick={props.questionModal}
        >
          Question Navigator
        </Button>
        <Button
          className="rounded-[10px] bg-[#ED5050] text-white hover:bg-[#ED5050]/90"
          onClick={props.confirmationModal}
        >
          Submit
        </Button>
      </div>
    </div>
  );
};

export default TopPanel;
