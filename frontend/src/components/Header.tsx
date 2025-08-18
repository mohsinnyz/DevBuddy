// D:\DevBuddy\frontend\src\components\Header.tsx

import Link from "next/link";
import { FaLaptopCode } from "react-icons/fa";

export default function Header() {
  return (
    <header className="w-full bg-gray-900 text-white shadow-sm p-4 sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between">
        {/* Left side: Icon and Name */}
        <div className="flex items-center space-x-2">
            <FaLaptopCode className="text-sky-500 text-2xl" />
          <Link href="/" className="text-2xl font-bold text-white">
            DevBuddy
          </Link>
        </div>

        {/* Right side: Navigation Links */}
        <nav>
          <ul className="flex space-x-4">
            <li>
              <Link
                href="https://github.com/mohsinnyz/DevBuddy/blob/main/README.md"
                className="text-gray-300 hover:text-sky-500 font-medium transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                About
              </Link>
            </li>
            <li>
              <Link
                href="https://linkedin.com/in/mohsinnyz"
                className="text-gray-300 hover:text-sky-500 font-medium transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                Contact Us
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}