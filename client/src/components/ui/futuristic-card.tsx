import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface FuturisticCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: 'blue' | 'green' | 'purple' | 'yellow' | 'red';
  active?: boolean;
}

export function FuturisticCard({ 
  children, 
  className, 
  glowColor = 'blue', 
  active = false 
}: FuturisticCardProps) {
  const glowClasses = {
    blue: 'shadow-blue-500/20 border-blue-500/30 bg-gradient-to-br from-blue-500/5 to-cyan-500/5',
    green: 'shadow-green-500/20 border-green-500/30 bg-gradient-to-br from-green-500/5 to-emerald-500/5',
    purple: 'shadow-purple-500/20 border-purple-500/30 bg-gradient-to-br from-purple-500/5 to-pink-500/5',
    yellow: 'shadow-yellow-500/20 border-yellow-500/30 bg-gradient-to-br from-yellow-500/5 to-orange-500/5',
    red: 'shadow-red-500/20 border-red-500/30 bg-gradient-to-br from-red-500/5 to-rose-500/5'
  };

  return (
    <div className={cn(
      "relative overflow-hidden rounded-lg border backdrop-blur-sm transition-all duration-300",
      active ? `shadow-lg ${glowClasses[glowColor]}` : "border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50",
      "hover:shadow-md hover:border-gray-300 dark:hover:border-gray-700",
      className
    )}>
      {/* Corner decorations */}
      <div className="absolute top-0 left-0 w-3 h-3 border-l-2 border-t-2 border-current opacity-30" />
      <div className="absolute top-0 right-0 w-3 h-3 border-r-2 border-t-2 border-current opacity-30" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-l-2 border-b-2 border-current opacity-30" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-r-2 border-b-2 border-current opacity-30" />
      
      {/* Scanning line animation */}
      {active && (
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-current to-transparent animate-pulse" />
        </div>
      )}
      
      {children}
    </div>
  );
}

interface MetricDisplayProps {
  value: string | number;
  label: string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'green' | 'purple' | 'yellow' | 'red';
}

export function MetricDisplay({ 
  value, 
  label, 
  icon, 
  trend = 'neutral', 
  color = 'blue' 
}: MetricDisplayProps) {
  const colorClasses = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400'
  };

  const trendSymbols = {
    up: '↗',
    down: '↘',
    neutral: '→'
  };

  return (
    <div className="flex items-center space-x-3">
      {icon && (
        <div className={cn("flex-shrink-0", colorClasses[color])}>
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline space-x-2">
          <span className={cn("text-2xl font-mono font-bold", colorClasses[color])}>
            {value}
          </span>
          <span className="text-xs opacity-60">
            {trendSymbols[trend]}
          </span>
        </div>
        <div className="text-xs text-muted-foreground uppercase tracking-wider">
          {label}
        </div>
      </div>
    </div>
  );
}

interface ProgressRingProps {
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  children?: ReactNode;
}

export function ProgressRing({ 
  progress, 
  size = 80, 
  strokeWidth = 4, 
  color = '#3b82f6',
  children 
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="opacity-20"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-300 drop-shadow-sm"
          style={{
            filter: `drop-shadow(0 0 6px ${color}40)`
          }}
        />
      </svg>
      {children && (
        <div className="absolute inset-0 flex items-center justify-center">
          {children}
        </div>
      )}
    </div>
  );
}