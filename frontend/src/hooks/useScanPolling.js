import { useState, useEffect, useRef } from "react";
import { cicdService } from "../services/cicdService";

/**
 * Hook for polling scan status
 * @param {string} scanType - Type of scan (zap, sonarqube, trivy)
 * @param {string} scanId - Scan ID to poll
 * @param {boolean} enabled - Whether polling is enabled
 * @param {number} interval - Polling interval in milliseconds (default: 5000)
 */
const useScanPolling = (scanType, scanId, enabled = true, interval = 5000) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!enabled || !scanId || !scanType) {
      return;
    }

    const pollStatus = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await cicdService.getScanStatus(scanType, scanId);
        setStatus(result);

        // Stop polling if scan is completed or failed
        if (result.status === "completed" || result.status === "failed") {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
        setError(err.message);
        // Stop polling on error
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } finally {
        setLoading(false);
      }
    };

    // Initial poll
    pollStatus();

    // Set up interval polling
    intervalRef.current = setInterval(pollStatus, interval);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [scanType, scanId, enabled, interval]);

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  return {
    status,
    loading,
    error,
    stopPolling,
    isPolling: intervalRef.current !== null,
  };
};

export default useScanPolling;
