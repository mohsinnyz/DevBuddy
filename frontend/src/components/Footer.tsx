// D:\DevBuddy\frontend\src\components\Footer.tsx

export default function Footer() {
  return (
    <footer className="w-full bg-gray-900 text-white p-4">
      <div className="container mx-auto text-center text-sm text-gray-400">
        © {new Date().getFullYear()} DevBuddy. All rights reserved.
      </div>
    </footer>
  );
}