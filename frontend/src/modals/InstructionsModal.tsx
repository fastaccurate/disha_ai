import { X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

type InstructionsModalProps = {
  open: boolean;
  close: () => void;
  submitHandler: () => void;
  data: string[];
};

const InstructionsModal = (props: InstructionsModalProps) => {
  const handleSubmit = () => {
    props.close();
    setTimeout(() => {
      props.submitHandler();
    }, 1000);
  };

  return (
    <Dialog open={props.open} onOpenChange={props.close}>
      <DialogContent className="sm:max-w-[700px]">
        <button
          onClick={props.close}
          className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </button>

        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Instructions</DialogTitle>
        </DialogHeader>

        <div className="flex flex-col items-start w-full">
          {props.data.map((instruction, index) => (
            <p key={index} className="text-base text-gray-700 mb-2">
              - {instruction}
            </p>
          ))}
        </div>

        <div className="flex justify-center mt-4">
          <Button variant="default" onClick={handleSubmit}>
            Start Assessment
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default InstructionsModal;
