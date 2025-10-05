import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface HudCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'warning' | 'info';
}

export function HudCard({ children, className, variant = 'primary' }: HudCardProps) {
  const variants = {
    primary: 'border-cyan-500/50 bg-cyan-500/5 shadow-cyan-500/20',
    secondary: 'border-blue-500/50 bg-blue-500/5 shadow-blue-500/20',
    warning: 'border-yellow-500/50 bg-yellow-500/5 shadow-yellow-500/20',
    info: 'border-purple-500/50 bg-purple-500/5 shadow-purple-500/20'
  };

  return (
    <div className={cn(
      "relative border-2 backdrop-blur-md rounded-lg p-4",
      "before:absolute before:top-0 before:left-0 before:w-3 before:h-3 before:border-l-2 before:border-t-2 before:border-current",
      "after:absolute after:bottom-0 after:right-0 after:w-3 after:h-3 after:border-r-2 after:border-b-2 after:border-current",
      variants[variant],
      className
    )}>
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent rounded-lg" />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}

interface HudButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  'data-testid'?: string;
}

export function HudButton({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  className,
  'data-testid': testId
}: HudButtonProps) {
  const variants = {
    primary: 'border-cyan-400 text-cyan-100 bg-cyan-500/10 hover:bg-cyan-500/20 shadow-cyan-500/30',
    secondary: 'border-blue-400 text-blue-100 bg-blue-500/10 hover:bg-blue-500/20 shadow-blue-500/30',
    danger: 'border-red-400 text-red-100 bg-red-500/10 hover:bg-red-500/20 shadow-red-500/30'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      data-testid={testId}
      className={cn(
        "relative border-2 backdrop-blur-md rounded transition-all duration-200",
        "before:absolute before:top-0 before:left-0 before:w-2 before:h-2 before:border-l before:border-t before:border-current",
        "after:absolute after:bottom-0 after:right-0 after:w-2 after:h-2 after:border-r after:border-b after:border-current",
        "focus:outline-none focus:ring-2 focus:ring-current/50",
        disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg active:scale-95',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </button>
  );
}

interface HexPanelProps {
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  active?: boolean;
  className?: string;
  onClick?: () => void;
}

export function HexPanel({ children, size = 'md', active = false, className, onClick }: HexPanelProps) {
  const sizes = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-20 h-20'
  };

  return (
    <div 
      onClick={onClick}
      className={cn(
        "relative flex items-center justify-center",
        "before:absolute before:inset-0 before:bg-gradient-to-br",
        active 
          ? "before:from-cyan-500/20 before:to-blue-500/20 before:border-2 before:border-cyan-400" 
          : "before:from-gray-500/10 before:to-gray-600/10 before:border before:border-gray-500",
        "backdrop-blur-md",
        onClick ? "cursor-pointer hover:scale-105 transition-transform" : "",
        sizes[size],
        className
      )}
    >
      <div className="relative z-10 text-center">
        {children}
      </div>
    </div>
  );
}

interface RadarDisplayProps {
  progress: number;
  size?: number;
  color?: string;
}

export function RadarDisplay({ progress, size = 80, color = '#00bcd4' }: RadarDisplayProps) {
  const radius = (size - 8) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circles */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius * 0.3}
          stroke="currentColor"
          strokeWidth="1"
          fill="none"
          opacity="0.2"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius * 0.6}
          stroke="currentColor"
          strokeWidth="1"
          fill="none"
          opacity="0.2"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth="1"
          fill="none"
          opacity="0.2"
        />
        
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="3"
          fill="none"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="drop-shadow-lg"
          style={{
            filter: `drop-shadow(0 0 8px ${color})`
          }}
        />
        
        {/* Center dot */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r="3"
          fill={color}
          className="animate-pulse"
        />
        
        {/* Scanning line */}
        <line
          x1={size / 2}
          y1={size / 2}
          x2={size / 2}
          y2="10"
          stroke={color}
          strokeWidth="2"
          opacity="0.8"
          className="animate-spin origin-center"
          style={{ animationDuration: '3s' }}
        />
      </svg>
    </div>
  );
}

interface MetricPanelProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
  icon?: ReactNode;
}

export function MetricPanel({ title, value, unit, trend, color = '#00bcd4', icon }: MetricPanelProps) {
  const trendIcons = {
    up: '↗',
    down: '↘',
    stable: '→'
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400 uppercase tracking-wider">{title}</span>
        {icon && <div className="text-current opacity-60">{icon}</div>}
      </div>
      <div className="flex items-baseline space-x-2">
        <span 
          className="text-2xl font-bold font-mono"
          style={{ color }}
        >
          {value}
        </span>
        {unit && <span className="text-sm text-gray-500">{unit}</span>}
        {trend && (
          <span className="text-sm opacity-60">{trendIcons[trend]}</span>
        )}
      </div>
    </div>
  );
}

interface WarningStripProps {
  children: ReactNode;
  className?: string;
}

export function WarningStrip({ children, className }: WarningStripProps) {
  return (
    <div className={cn(
      "relative bg-gradient-to-r from-yellow-600/20 via-yellow-500/30 to-yellow-600/20",
      "border-y border-yellow-400/50 p-3",
      "before:absolute before:left-0 before:top-0 before:bottom-0 before:w-4",
      "before:bg-gradient-to-r before:from-transparent before:via-yellow-500/50 before:to-transparent",
      "before:border-l-2 before:border-yellow-400",
      "after:absolute after:right-0 after:top-0 after:bottom-0 after:w-4",
      "after:bg-gradient-to-l after:from-transparent after:via-yellow-500/50 after:to-transparent",
      "after:border-r-2 after:border-yellow-400",
      className
    )}>
      <div className="flex items-center justify-center text-yellow-100 font-medium">
        <div className="flex items-center space-x-2">
          <span>⚠</span>
          {children}
          <span>⚠</span>
        </div>
      </div>
    </div>
  );
}