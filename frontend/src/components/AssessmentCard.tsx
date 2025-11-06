import { useState } from "react";
import { Button } from "@/components/ui/button";
import InstructionsModal from "@/modals/InstructionsModal";

interface AssessmentProps {
  assessmentNumber: number;
  assessmentName?: string;
  assessmentInstructions?: string[];
  bgColor?: string;
  startHandler?: () => void;
  assessmentGenId: string;
}

export const AssessmentCard = (props: AssessmentProps) => {
  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <>
      <div className="flex flex-col w-[420px] h-[200px] bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-lg hover:shadow-2xl border border-gray-100 overflow-hidden transition-all duration-300 hover:-translate-y-1">
        {/* header */}
        <div
          className="relative px-8 py-6"
          style={{ backgroundColor: props.bgColor || "#2059EE" }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-white/25 backdrop-blur-sm flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">
                  {props.assessmentNumber}
                </span>
              </div>
              <h2 className="text-xl font-bold text-white">
                {props.assessmentName || "Assessment"}
              </h2>
            </div>
          </div>
        </div>

        {/* button section */}
        {props.startHandler && (
          <div className="flex-1 flex items-end p-6">
            <Button
              className="w-full rounded-xl text-base font-semibold bg-gray-900 hover:bg-gray-800 text-white transition-all duration-200 h-12 shadow-md hover:shadow-lg"
              onClick={handleOpen}
            >
              Start Assessment →
            </Button>
          </div>
        )}
      </div>

      <InstructionsModal
        open={open}
        close={handleClose}
        submitHandler={props.startHandler || (() => {})}
        data={props.assessmentInstructions || []}
      />
    </>
  );
};
