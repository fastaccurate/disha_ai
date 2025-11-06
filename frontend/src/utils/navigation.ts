const handleNext = (
  transformedList: any[],
  currentQuestion: { section: any; questionId: any },
  setCurrentQuestion: {
    (value: any): void;
    (value: any): void;
    (value: any): void;
    (arg0: { section: any; questionId: any }): void;
  }
) => {
  const currentIndex = transformedList.findIndex(
    (item) =>
      item.section === currentQuestion.section &&
      item.question_id === currentQuestion.questionId
  );
  if (currentIndex < transformedList.length - 1) {
    const nextQuestion = transformedList[currentIndex + 1];
    setCurrentQuestion({
      section: nextQuestion.section,
      questionId: nextQuestion.question_id,
    });
  }
};

const handlePrevious = (
  transformedList: any[],
  currentQuestion: { section: any; questionId: any },
  setCurrentQuestion: {
    (value: any): void;
    (arg0: { section: any; questionId: any }): void;
  }
) => {
  const currentIndex = transformedList.findIndex(
    (item) =>
      item.section === currentQuestion.section &&
      item.question_id === currentQuestion.questionId
  );
  if (currentIndex > 0) {
    const prevQuestion = transformedList[currentIndex - 1];
    setCurrentQuestion({
      section: prevQuestion.section,
      questionId: prevQuestion.question_id,
    });
  }
};

export { handleNext, handlePrevious };
