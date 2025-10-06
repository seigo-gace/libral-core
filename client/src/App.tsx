import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider, QueryErrorResetBoundary } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Dashboard from "@/pages/dashboard";
import DashboardHud from "@/pages/dashboard-hud";
import AdminDashboard from "@/pages/admin-dashboard";
import UserMenu from "@/pages/user-menu";
import HudUserMenu from "@/pages/hud-user-menu";
import CommunicationGateway from "@/pages/communication-gateway";
import UserManagement from "@/pages/user-management";
import EventManagement from "@/pages/event-management";
import PaymentManagement from "@/pages/payment-management";
import PaymentDemo from "@/pages/payment-demo";
import APIHub from "@/pages/api-hub";
import DatabaseManagement from "@/pages/database-management";
import ContainerManagement from "@/pages/container-management";
import GpgConfig from "@/pages/gpg-config";
import Analytics from "@/pages/analytics";
import Settings from "@/pages/settings";
import Logs from "@/pages/logs";
import NotFound from "@/pages/not-found";
import Monitor from "@/pages/Monitor";
import Control from "@/pages/Control";
import Creation from "@/pages/Creation";

function Router() {
  return (
    <Switch>
      <Route path="/" component={DashboardHud} />
      <Route path="/monitor" component={Monitor} />
      <Route path="/control" component={Control} />
      <Route path="/creation" component={Creation} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/dashboard-hud" component={DashboardHud} />
      <Route path="/admin-dashboard" component={AdminDashboard} />
      <Route path="/user-menu" component={UserMenu} />
      <Route path="/hud-user-menu" component={HudUserMenu} />
      <Route path="/communication-gateway" component={CommunicationGateway} />
      <Route path="/user-management" component={UserManagement} />
      <Route path="/event-management" component={EventManagement} />
      <Route path="/payment-management" component={PaymentManagement} />
      <Route path="/payment-demo" component={PaymentDemo} />
      <Route path="/api-hub" component={APIHub} />
      <Route path="/database-management" component={DatabaseManagement} />
      <Route path="/container-management" component={ContainerManagement} />
      <Route path="/gpg-config" component={GpgConfig} />
      <Route path="/analytics" component={Analytics} />
      <Route path="/settings" component={Settings} />
      <Route path="/logs/:moduleId" component={Logs} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <QueryErrorResetBoundary>
        {({ reset }) => (
          <TooltipProvider>
            <div className="dark">
              <Toaster />
              <Router />
            </div>
          </TooltipProvider>
        )}
      </QueryErrorResetBoundary>
    </QueryClientProvider>
  );
}

export default App;
