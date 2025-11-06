import EvalAPI from "../apis/EvalAPI";
import { ANSWER_TYPE } from "@/pages/Assessment";

export const useFetchQuestions = (
  assessmentId: string | null,
  currentQuestion: { section: string; questionId: number },
  questions: any[],
  setQuestion: (question: any) => void,
  setSelectedOption: (option: number) => void,
  setSelectedMMcqOption: (options: Record<number, number | null>) => void,
  setWriteupAnswer: (answer: string) => void,
  setRecordedAudioURL: (url: string | null) => void,
  totalAttemptedQuestionsMapping: Record<number, any>
) => {
  const fetchQuestions = async () => {
    if (assessmentId && questions.length > 0) {
      try {
        const data = await EvalAPI.getQuestions(
          Number(assessmentId),
          currentQuestion.questionId
        );
        if (data) {
          setQuestion(data);
          const previouslyAttempted =
            totalAttemptedQuestionsMapping[currentQuestion.questionId];

          if (data.answer_type === ANSWER_TYPE.MCQ) {
            setSelectedOption(
              previouslyAttempted !== undefined ? previouslyAttempted : -1
            );
          }

          if (data.answer_type === ANSWER_TYPE.MMCQ) {
            setSelectedMMcqOption(
              previouslyAttempted !== undefined &&
                previouslyAttempted.length > 0
                ? previouslyAttempted.filter((option: number) => option !== -1)
                : {}
            );
          }

          if (data.answer_type === ANSWER_TYPE.SUBJECTIVE) {
            setWriteupAnswer(
              previouslyAttempted !== undefined
                ? previouslyAttempted.toString()
                : ""
            );
          }

          if (data.answer_type === ANSWER_TYPE.VOICE) {
            setRecordedAudioURL(previouslyAttempted || null);
          }
        }
      } catch (error) {
        console.error("Error fetching question:", error);
      }
    }
  };

  return { fetchQuestions };
};
