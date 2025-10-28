import { useState } from "react";
import { LandingPage } from "./components/LandingPage";
import { LoginForm } from "./components/LoginForm";
import { Layout } from "./components/Layout";
import { Dashboard } from "./components/Dashboard";
import { InventoryManager } from "./components/InventoryManager";
import { InsumosManager } from "./components/InsumosManager";
import { RecipeManager } from "./components/RecipeManager";
import { ProductManager } from "./components/ProductManager";
import { SupplierManager } from "./components/SupplierManager";
import { UserManager } from "./components/UserManager";
import { AlertsManager } from "./components/AlertsManager";
import { ReportsManager } from "./components/ReportsManager";
import { SettingsManager } from "./components/SettingsManager";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState("");
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [showLanding, setShowLanding] = useState(false);

  const handleLogin = (email: string) => {
    setCurrentUser(email);
    setIsLoggedIn(true);
    setShowLanding(false);
  };

  const handleGetStarted = () => {
    setShowLanding(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser("");
    setCurrentPage("dashboard");
    setShowLanding(true);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "inventory":
        return <InventoryManager />;
      case "insumos":
        return <InsumosManager />;
      case "recipes":
        return <RecipeManager />;
      case "products":
        return <ProductManager />;
      case "suppliers":
        return <SupplierManager />;
      case "users":
        return <UserManager />;
      case "alerts":
        return <AlertsManager />;
      case "reports":
        return <ReportsManager />;
      case "settings":
        return <SettingsManager />;
      default:
        return <Dashboard />;
    }
  };

  if (showLanding) {
    return <LandingPage onGetStarted={handleGetStarted} />;
  }

  if (!isLoggedIn) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <Layout
      currentPage={currentPage}
      onPageChange={setCurrentPage}
      onLogout={handleLogout}
      username={currentUser}
    >
      {renderCurrentPage()}
    </Layout>
  );
}