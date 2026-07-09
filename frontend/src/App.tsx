import { Route, Routes } from "react-router-dom";

import { GrainOverlay } from "./components/GrainOverlay";
import LandingPage from "./pages/LandingPage";
import SeatMapPage from "./pages/SeatMapPage";
import CheckoutPage from "./pages/CheckoutPage";
import ConfirmationPage from "./pages/ConfirmationPage";

export default function App() {
  return (
    <>
      <GrainOverlay />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/events/:id" element={<SeatMapPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/booking/:reference" element={<ConfirmationPage />} />
      </Routes>
    </>
  );
}
