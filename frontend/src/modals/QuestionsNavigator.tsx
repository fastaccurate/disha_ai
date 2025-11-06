import { QuestionNavigatorModalProps } from "./types";

const QuestionNavigatorModal = (props: QuestionNavigatorModalProps) => {
  const handleNavigatorClick = (section: string, questionId: number) => {
    props.setCurrentQuestion({ section, questionId });
    props.close();
  };

  return (
    <div
      aria-labelledby="question-navigator-modal-title"
      aria-describedby="question-navigator-modal-description"
      className={`fixed inset-0 z-50 flex items-center justify-center ${
        props.open ? "block" : "hidden"
      }`}
    >
      <div
        className="fixed inset-0 bg-black opacity-50"
        onClick={props.close}
      ></div>
      <div className="relative z-10">
        <div className="flex flex-col items-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-max max-w-2xl bg-white shadow-lg p-4 rounded-lg">
          {/* question list  */}
          <div className="grid grid-cols-10 gap-2 mt-5">
            {props.transformedQuestionsList.map(
              (
                question: { question_id: number; section: string },
                index: number
              ) => {
                const isCurrentQuestion =
                  question.question_id === props.currentQuestion.questionId;
                const isAttempted =
                  props.attemptedQuestionsMapping[question.question_id];
                return (
                  <div
                    key={index}
                    className={`w-10 h-10 rounded-lg flex justify-center items-center cursor-pointer hover:bg-blue-600 hover:text-white transition-colors ${
                      isCurrentQuestion
                        ? "bg-blue-600 text-white"
                        : isAttempted
                        ? "bg-green-500"
                        : "bg-gray-300"
                    }`}
                    onClick={() =>
                      handleNavigatorClick(
                        question.section,
                        question.question_id
                      )
                    }
                  >
                    <span>
                      {index !== null && index !== undefined ? index + 1 : ""}
                    </span>
                  </div>
                );
              }
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionNavigatorModal;
