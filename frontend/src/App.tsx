import { Route, Routes } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import SeatMapPage from "./pages/SeatMapPage";
import CheckoutPage from "./pages/CheckoutPage";
import ConfirmationPage from "./pages/ConfirmationPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/events/:id" element={<SeatMapPage />} />
      <Route path="/checkout" element={<CheckoutPage />} />
      <Route path="/booking/:reference" element={<ConfirmationPage />} />
    </Routes>
  );
}
