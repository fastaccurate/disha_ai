import { useNavigate } from "react-router-dom";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

type BreadCrumbPage = {
  name: string;
  route: string;
  onClick?: () => void;
};

type BreadCrumbProps = {
  previousPages: BreadCrumbPage[];
  currentPageName: string;
};

function BreadCrumb(props: BreadCrumbProps) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col bg-white p-5">
      <Breadcrumb>
        <BreadcrumbList>
          {props.previousPages.map((page, index) => (
            <>
              <BreadcrumbItem key={index}>
                <BreadcrumbLink
                  className="text-blue-600 font-semibold hover:underline"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate(page.route);
                    if (page.onClick) {
                      page.onClick();
                    }
                  }}
                >
                  {page.name}
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator>›</BreadcrumbSeparator>
            </>
          ))}
          <BreadcrumbItem>
            <BreadcrumbPage className="text-black font-semibold">
              {props.currentPageName}
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    </div>
  );
}

export default BreadCrumb;
