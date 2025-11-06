import { useEffect, useState, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import BreadCrumb from "@/components/BreadCrumb";
import EvalAPI from "@/apis/EvalAPI";
import { useToast } from "@/hooks/use-toast";
import { ROUTES } from "@/configs/routes";

const breadcrumbPreviousPages = [
  {
    name: "Home",
    route: ROUTES.HOME,
  },
];

type AssessmentResult = {
  assessment_id: number;
  assessment_name: string;
  course_code: string;
  module_name: string;
  percentage: number;
  total_obtained: number;
  grand_total: number;
  last_attempted: string;
  status: number;
};

const AssessmentsResults = () => {
  const [assessmentsResults, setAssessmentsResults] = useState<
    AssessmentResult[]
  >([]);
  const location = useLocation();
  const { toast } = useToast();

  const hasEvaluatingAssessmentToday = useCallback(() => {
    const today = new Date().toISOString().split("T")[0];
    return assessmentsResults.some(
      (assessment) =>
        assessment.status === 3 &&
        assessment.last_attempted?.split("T")[0] === today
    );
  }, [assessmentsResults]);

  const fetchAssessmentsResults = async () => {
    const resp = await EvalAPI.getAssessmentsResults();
    setAssessmentsResults(resp.attempted_list);
  };

  useEffect(() => {
    fetchAssessmentsResults();
  }, []);

  useEffect(() => {
    let pollInterval: NodeJS.Timeout;
    if (hasEvaluatingAssessmentToday()) {
      pollInterval = setInterval(() => {
        fetchAssessmentsResults();
      }, 5000);
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [hasEvaluatingAssessmentToday]);

  useEffect(() => {
    const isTestEnded = location.state?.isTestEnded;

    if (isTestEnded) {
      toast({
        description: "Your assessment result will appear here shortly",
        duration: 5000,
      });
    }
  }, [location, toast]);

  return (
    <div className="flex flex-col min-h-screen w-full bg-[#EFF6FF] p-8 pt-6">
      <BreadCrumb
        currentPageName="Results"
        previousPages={breadcrumbPreviousPages}
      />

      <div className="flex flex-col gap-4 h-full pt-4">
        <h1 className="text-2xl font-bold text-black">Assessment Results</h1>

        <p className="text-base text-[#8EA1B3] w-4/5 mb-4">
          Here are the results of the assessments you have attempted.
        </p>

        <div className="rounded-md border bg-white shadow-sm">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50 hover:bg-gray-50">
                <TableHead className="font-bold text-gray-700 py-4">
                  Assessment
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Date Last Attempted
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Course Code
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Module
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Status
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Max. Marks
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Obt. Marks
                </TableHead>
                <TableHead className="font-bold text-gray-700 py-4">
                  Percentage
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {assessmentsResults.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={8}
                    className="text-center text-gray-500 py-8"
                  >
                    No assessments attempted yet.
                  </TableCell>
                </TableRow>
              ) : (
                assessmentsResults.map((row) => (
                  <TableRow
                    key={row.assessment_id}
                    className="border-b transition-colors hover:bg-gray-50/50"
                  >
                    <TableCell className={`py-3 cursor-default`}>
                      {row.assessment_name}
                    </TableCell>
                    <TableCell className="py-3">
                      {row.last_attempted
                        ? new Date(row.last_attempted).toDateString() +
                          new Date(row.last_attempted)
                            .toLocaleString()
                            .split(",")[1]
                        : "N/A"}
                    </TableCell>
                    <TableCell className="py-3">{row.course_code}</TableCell>
                    <TableCell className="py-3">{row.module_name}</TableCell>
                    <TableCell className="py-3">
                      {row.status === 2 ? (
                        <span className="text-green-600 font-medium">
                          Completed
                        </span>
                      ) : row.status === 3 ? (
                        <span className="text-amber-600 font-medium">
                          Evaluating
                        </span>
                      ) : row.status === 4 ? (
                        <span className="text-red-600 font-medium">
                          Abandoned
                        </span>
                      ) : null}
                    </TableCell>
                    <TableCell className="py-3">
                      {row.status === 3 ? (
                        <Skeleton className="w-full h-4" />
                      ) : row.status === 4 ? (
                        "-"
                      ) : (
                        <span className="font-medium">{row.grand_total}</span>
                      )}
                    </TableCell>
                    <TableCell className="py-3">
                      {row.status === 3 ? (
                        <Skeleton className="w-full h-4" />
                      ) : row.status === 4 ? (
                        "-"
                      ) : (
                        <span className="font-medium">
                          {row.total_obtained}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="py-3">
                      {row.status === 3 ? (
                        <Skeleton className="w-full h-4" />
                      ) : row.status === 4 ? (
                        "-"
                      ) : (
                        <span
                          className={`font-medium ${
                            row.percentage >= 60
                              ? "text-green-600"
                              : row.percentage >= 40
                              ? "text-amber-600"
                              : "text-red-600"
                          }`}
                        >
                          {row.percentage}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
};

export default AssessmentsResults;
