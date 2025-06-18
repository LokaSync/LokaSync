import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Main from "@/components/layout/Main";
import { ScrollToTop } from "@/components/ui/scroll-to-top";
import { usePageTitle } from "@/hooks/usePageTitle";
import { LocalLogManagementTable } from "@/components/tables/LocalLogManagementTable";
import { locallogController } from "@/controllers";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Squares from "@/components/background/Squares";
import type { FirmwareLocalLog, LocalLogsListParams, LocalLogFilterOptions } from "@/types";

export default function LocalLog() {
  const [logs, setLogs] = useState<FirmwareLocalLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total_data: 0,
    total_page: 0,
  });
  const [filterOptions, setFilterOptions] = useState<LocalLogFilterOptions>({ 
    flash_statuses: [],
  });
  const [filters, setFilters] = useState({
    flash_status: "",
  });

  usePageTitle("Local Log Updates");

  // Use useCallback to memoize fetchLogs function
  const fetchLogs = useCallback(
    async (params?: Partial<LocalLogsListParams>) => {
      try {
        setLoading(true);
        setError("");

        // Build clean params object - only include non-empty values
        const requestParams: LocalLogsListParams = {
          page: pagination.page,
          page_size: pagination.page_size,
        };

        // Only add filter params if they have values
        if (filters.flash_status && filters.flash_status !== "") {
          requestParams.flash_status = filters.flash_status;
        }

        // Merge with any additional params
        const finalParams = { ...requestParams, ...params };

        const response = await locallogController.getAllLogs(finalParams);

        setLogs(response.data);
        setPagination({
          page: response.page,
          page_size: response.page_size,
          total_data: response.total_data,
          total_page: response.total_page,
        });
        setFilterOptions(response.filter_options);
      } catch (error: unknown) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "An unexpected error occurred";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.page_size, filters],
  );

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleRefresh = () => {
    fetchLogs();
  };

  const handlePageChange = (newPage: number) => {
    setPagination((prev) => ({ ...prev, page: newPage }));
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPagination((prev) => ({ ...prev, page_size: newPageSize, page: 1 }));
  };

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
    setPagination((prev) => ({ ...prev, page: 1 }));
  };

  return (
    <div className="min-h-screen flex flex-col bg-background relative">
      {/* Squares Background Animation */}
      <div className="absolute inset-0 z-0">
        <Squares speed={0.5} squareSize={12} direction="diagonal" />
      </div>

      {/* Content Layer */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />
        <Main>
          <div className="space-y-6">
            {/* Header Section */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold">Local Log Updates</h1>
                <p className="text-sm text-muted-foreground mt-1">
                  View and manage firmware local update logs in real-time
                </p>
              </div>

              <div className="flex gap-2">
                <Button onClick={handleRefresh} disabled={loading}>
                  <RefreshCw
                    className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
                  />
                  Refresh
                </Button>
              </div>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Log Management Table */}
            <LocalLogManagementTable
              logs={logs}
              loading={loading}
              pagination={pagination}
              filterOptions={filterOptions}
              filters={filters}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
              onFilterChange={handleFilterChange}
              onRefresh={fetchLogs}
            />
          </div>
        </Main>
        <Footer />

        {/* Scroll to Top Button */}
        <ScrollToTop />
      </div>
    </div>
  );
}
