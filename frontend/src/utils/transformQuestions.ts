export const transformQuestions = (questionList: any[]) => {
  const transformedQuestions: { section: any; question_id: any }[] = [];

  questionList?.forEach((section: { questions: any[]; section: any }) => {
    section.questions.forEach((questionId: any) => {
      transformedQuestions.push({
        section: section.section,
        question_id: questionId,
      });
    });
  });

  return transformedQuestions;
};
