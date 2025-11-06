import EvalAPI from "../apis/EvalAPI";
import { transformQuestions } from "../utils/transformQuestions";

export const useFetchAttemptedQuestions = (
  assessmentId: string | null,
  currentQuestionId: string | null,
  setTotalAttemptedQuestionsMapping: (mapping: Record<number, any>) => void,
  setQuestions: (questions: any[]) => void,
  setCurrentQuestion: (question: {
    section: string;
    questionId: number;
  }) => void
) => {
  const fetchAttemptedQuestions = async () => {
    if (assessmentId) {
      const data = await EvalAPI.getState(Number(assessmentId));
      if (data) {
        const attemptedQuestionsMap = data.attempted_questions.reduce(
          (acc: any, curr: any) => {
            if (curr.answer_text) {
              acc[curr.question_id] = curr.answer_text;
            } else if (
              curr.multiple_mcq_answer &&
              curr.multiple_mcq_answer.length > 0
            ) {
              acc[curr.question_id] = curr.multiple_mcq_answer;
            } else if (curr.answer_audio_url) {
              acc[curr.question_id] = curr.answer_audio_url;
            } else {
              acc[curr.question_id] = curr.mcq_answer;
            }
            return acc;
          },
          {}
        );

        setTotalAttemptedQuestionsMapping(attemptedQuestionsMap);

        const transformedQuestions = transformQuestions(data.question_list);

        setQuestions(transformedQuestions);

        const initialQuestion =
          transformedQuestions.find(
            (q) => q.question_id === Number(currentQuestionId)
          ) || transformedQuestions[0];

        setCurrentQuestion({
          section: initialQuestion.section,
          questionId: initialQuestion.question_id,
        });
      }
    }
  };

  return { fetchAttemptedQuestions };
};
