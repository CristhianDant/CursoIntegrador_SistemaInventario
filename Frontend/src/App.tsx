import { useState } from "react";
import { LoginForm } from "./components/LoginForm";
import { Layout } from "./components/Layout";
import { Dashboard } from "./components/Dashboard";
import { InventoryManager } from "./components/InventoryManager";
import { PurchaseOrderManager } from "./components/PurchaseOrderManager";
import { RecipeManager } from "./components/RecipeManager";
import { ProductManager } from "./components/ProductManager";
import { SupplierManager } from "./components/SupplierManager";
import { UserManager } from "./components/UserManager";
import { AlertsManager } from "./components/AlertsManager";
import { ReportsManager } from "./components/ReportsManager";
import { SettingsManager } from "./components/SettingsManager";
import { SupplyEntryManager } from "./components/SupplyEntryManager";
import { TypewriterSplash } from './components/TypewriterSplash';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState("");
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [showLanding, setShowLanding] = useState(false);
  const [showSplash, setShowSplash] = useState(true);

  const handleLogin = (email: string) => {
    setCurrentUser(email);
    setIsLoggedIn(true);
    setShowLanding(false);
  };

  const handleSplashEnd = () => {
    // Cuando la animación de TypewriterSplash termina, ocultamos el splash
    setShowSplash(false);
  };

  const handleGetStarted = () => {
    setShowLanding(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser("");
    setCurrentPage("dashboard");
    setShowLanding(true);
    setShowSplash(true);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "inventory":
        return <InventoryManager />;
      case "recipes":
        return <RecipeManager />;
      case "purchase-orders":
        return <PurchaseOrderManager />;
      case "supply-entry":
        return <SupplyEntryManager />;
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

  if (showSplash) {
    return <TypewriterSplash onAnimationEnd={handleSplashEnd} />;
  }

  if (showLanding) {
    return <LoginForm onLogin={handleGetStarted} />;
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