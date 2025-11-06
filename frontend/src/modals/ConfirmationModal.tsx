import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { images } from "../assets";

type ConfirmationModalProps = {
  open: boolean;
  close: () => void;
  submit: () => void;
};

const ConfirmationModal = (props: ConfirmationModalProps) => {
  return (
    <Dialog open={props.open} onOpenChange={props.close}>
      <DialogContent className="w-[700px] p-6 flex flex-col items-center">
        <img
          src={images.confirmSubmitVector}
          alt="Are you sure?"
          className="w-[150px] h-[150px] mx-auto object-contain"
        />

        <DialogTitle className="mt-4 text-2xl font-semibold text-center">
          Are you sure you want to end the assessment?
        </DialogTitle>

        <DialogDescription className="mt-4 text-base text-center w-4/5">
          You can't go back once you end the assessment.
        </DialogDescription>

        <div className="flex flex-row gap-4 mt-8">
          {["Nah, Go back", "Yes, Next"].map((option) => (
            <Button
              key={option}
              variant="default"
              className="bg-[#2059EE] hover:bg-[#2059EE] rounded-lg"
              onClick={option === "Nah, Go back" ? props.close : props.submit}
            >
              <span className="text-sm normal-case">{option}</span>
            </Button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ConfirmationModal;
