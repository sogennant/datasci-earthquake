"use client";

import { useEffect, useState } from "react";
import { Box, Text, VStack, HStack, Badge } from "@chakra-ui/react";

interface PerformanceMetrics {
  endpoint: string;
  responseTime: number;
  timestamp: number;
  cacheStatus: "HIT" | "MISS" | "UNKNOWN";
}

export default function PerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only show in development or when explicitly enabled
    setIsVisible(
      process.env.NODE_ENV === "development" ||
        localStorage.getItem("showPerformanceMonitor") === "true"
    );
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    // Monitor API calls
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const startTime = performance.now();
      const url = args[0] as string;

      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        const responseTime = endTime - startTime;

        // Extract cache status from headers
        const cacheStatus =
          (response.headers.get("X-Cache") as "HIT" | "MISS" | "UNKNOWN") ||
          "UNKNOWN";

        if (url.includes("/api/")) {
          const newMetric: PerformanceMetrics = {
            endpoint: url.split("/api/")[1] || "unknown",
            responseTime: Math.round(responseTime),
            timestamp: Date.now(),
            cacheStatus,
          };

          setMetrics((prev) => [newMetric, ...prev.slice(0, 9)]); // Keep last 10
        }

        return response;
      } catch (error) {
        const endTime = performance.now();
        const responseTime = endTime - startTime;

        if (url.includes("/api/")) {
          const newMetric: PerformanceMetrics = {
            endpoint: url.split("/api/")[1] || "unknown",
            responseTime: Math.round(responseTime),
            timestamp: Date.now(),
            cacheStatus: "UNKNOWN",
          };

          setMetrics((prev) => [newMetric, ...prev.slice(0, 9)]);
        }

        throw error;
      }
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, [isVisible]);

  if (!isVisible) return null;

  const getAverageResponseTime = () => {
    if (metrics.length === 0) return 0;
    const total = metrics.reduce((sum, m) => sum + m.responseTime, 0);
    return Math.round(total / metrics.length);
  };

  const getCacheHitRate = () => {
    if (metrics.length === 0) return 0;
    const hits = metrics.filter((m) => m.cacheStatus === "HIT").length;
    return Math.round((hits / metrics.length) * 100);
  };

  return (
    <Box
      position="fixed"
      bottom="4"
      right="4"
      bg="white"
      border="1px"
      borderColor="gray.200"
      borderRadius="md"
      p="3"
      boxShadow="lg"
      maxW="400px"
      zIndex="1000"
    >
      <VStack align="stretch">
        <Text fontSize="sm" fontWeight="bold" color="gray.700">
          API Performance Monitor
        </Text>

        <HStack justify="space-between" fontSize="xs">
          <Text>Avg Response: {getAverageResponseTime()}ms</Text>
          <Text>Cache Hit: {getCacheHitRate()}%</Text>
        </HStack>

        <Box maxH="200px" overflowY="auto">
          {metrics.map((metric, index) => (
            <HStack key={index} justify="space-between" fontSize="xs" py="1">
              <Text maxW="200px">{metric.endpoint}</Text>
              <HStack>
                <Text>{metric.responseTime}ms</Text>
                <Badge
                  size="sm"
                  colorScheme={
                    metric.cacheStatus === "HIT" ? "green" : "orange"
                  }
                >
                  {metric.cacheStatus}
                </Badge>
              </HStack>
            </HStack>
          ))}
        </Box>

        <Text fontSize="xs" color="gray.500" textAlign="center">
          {metrics.length} recent calls
        </Text>
      </VStack>
    </Box>
  );
}
