export const ROUTES = {
  HOME: "/",
  START: "/assessment-start",
  RESULTS: "/assessment-results",
} as const;

export const getAssessmentStartRoute = (
  assessmentId: string,
  questionId: string
) => `${ROUTES.START}?id=${assessmentId}&questionId=${questionId}`;
