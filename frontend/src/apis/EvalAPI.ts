import apiConfig from "../configs/api";
import api from "../configs/axios";

export interface AssessmentReportResponse {
  data: {
    assessment_info: {
      assessment_id: string;
      assessment_name: string;
    };
    performance_overview: {
      feedback: string;
      score: number;
    };
    performance_metrics: CategoryPerformance[];
    sections: AssessmentResultSection[];
  };
  status: ReportStatus;
}

export enum ReportStatus {
  CREATION_PENDING = 0,
  IN_PROGRESS = 1,
  COMPLETED = 2,
  EVALUATION_PENDING = 3,
  ABANDONED = 4,
}

export interface CategoryPerformance {
  category: string;
  score: number;
}

export interface AssessmentResultSection {
  name: string;
  metrics: Metric[];
}

export interface Metric {
  name: string;
  total_score: number;
  obtained_score: string;
}

const EvalAPI = {
  getAssessmentConfigs: async function () {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/assessment-configs`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  startAssessment: async function (type: number) {
    console.log(type);

    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/start-assessment`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        assessment_generation_id: type,
      },
      withCredentials: true,
    });

    console.log(response.data);

    return response.data.data;
  },
  getAllAssessmentsData: async function () {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/assessment-display-data`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  getQuestions: async function (assessmentId: number, questionId: number) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/questions?assessment_id=${assessmentId}&question_id=${questionId}`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  getState: async function (assessmentId: number) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/assessment-state?assessment_id=${assessmentId}`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  submitAnswerMCQ: async function (
    assessmentId: number,
    questionId: number,
    answer: string,
    section: number
  ) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/submit-assessment-answer-mcq`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        assessment_id: assessmentId,
        question_id: questionId,
        mcq_answer: answer,
        section: section,
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  submitAnswerWriteUp: async function (
    assessmentId: number,
    questionId: number,
    answer: string,
    section: number
  ) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/submit-assessment-answer-subjective`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        question_id: questionId,
        answer_text: answer,
        assessment_id: assessmentId,
        section: section,
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  submitAnswerMMCQ: async function (
    questionId: number,
    assessmentId: number,
    multiple_mcq_answer: number[],
    section: number
  ) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/submit-assessment-answer-mmcq`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        question_id: questionId,
        assessment_id: assessmentId,
        multiple_mcq_answer: multiple_mcq_answer,
        section: section,
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  submitSpeakingAnswer: async function (
    questionId: number,
    assessmentId: number
  ) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/submit-assessment-answer-voice`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        question_id: questionId,
        assessment_id: assessmentId,
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  uploadAudioFile: async function (
    recordedUrl: string,
    uploadUrl: string
  ): Promise<boolean> {
    if (!recordedUrl) return false;

    const resp = await fetch(recordedUrl);
    const file = await resp.blob();

    const response = await fetch(uploadUrl, {
      method: "PUT",
      headers: {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": "audio/wav",
      },
      body: file,
    });

    if (response && response !== undefined && response.ok) {
      console.log(response);
      console.log("Audio file uploaded successfully!");
      return true;
    } else {
      console.error(
        "Failed to upload audio file:",
        response.status,
        response.statusText
      );
      return false;
    }
  },
  exitAssessment: async function (assessmentId: number) {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/close-assessment`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        assessment_id: assessmentId,
      },
      withCredentials: true,
    });

    return response.data.data;
  },
  getAssessmentsResults: async function () {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/assessment-history`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    // console.log("Assessments results:", response.data);
    return response.data.data;
  },
  getSasUrlToUploadResume: async function () {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/generate-azure-storage-url`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });
    return response.data;
  },
  getSingleAssessmentsResult: async function (
    assessmentId: string
  ): Promise<AssessmentReportResponse> {
    const response = await api.request({
      url: `${apiConfig.EVAL_URL_LMS}/fetch-report?assessmentId=${assessmentId}`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    // console.log("Assessments results:", response.data);
    return response.data.data;
  },
};

export default EvalAPI;
