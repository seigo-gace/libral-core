import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Dashboard from "@/pages/dashboard";
import CommunicationGateway from "@/pages/communication-gateway";
import UserManagement from "@/pages/user-management";
import EventManagement from "@/pages/event-management";
import PaymentManagement from "@/pages/payment-management";
import PaymentDemo from "@/pages/payment-demo";
import APIHub from "@/pages/api-hub";
import DatabaseManagement from "@/pages/database-management";
import ContainerManagement from "@/pages/container-management";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/communication-gateway" component={CommunicationGateway} />
      <Route path="/user-management" component={UserManagement} />
      <Route path="/event-management" component={EventManagement} />
      <Route path="/payment-management" component={PaymentManagement} />
      <Route path="/payment-demo" component={PaymentDemo} />
      <Route path="/api-hub" component={APIHub} />
      <Route path="/database-management" component={DatabaseManagement} />
      <Route path="/container-management" component={ContainerManagement} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <div className="dark">
          <Toaster />
          <Router />
        </div>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
