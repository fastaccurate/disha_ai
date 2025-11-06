import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface MiddlePanelProps {
  handlePrevious: () => void;
  handleNext: () => void;
  transformedList: any;
  currentQuestion: any;
}

const MiddlePanel = (props: MiddlePanelProps) => {
  const currentIndex = props.transformedList.findIndex(
    (item: { section: any; question_id: any }) =>
      item.section === props.currentQuestion.section &&
      item.question_id === props.currentQuestion.questionId
  );

  return (
    <div className="flex flex-row items-center justify-between w-full p-2.5 bg-white rounded-t-lg border-b-2">
      <Button
        variant="ghost"
        size="icon"
        onClick={props.handlePrevious}
        disabled={currentIndex === 0}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      <span className="bg-black text-white text-base px-3 py-1.5 rounded-lg">
        {currentIndex + 1}
      </span>

      <Button
        variant="ghost"
        size="icon"
        onClick={props.handleNext}
        disabled={currentIndex === props.transformedList.length - 1}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default MiddlePanel;
