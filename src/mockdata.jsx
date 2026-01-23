import { FiFileText, FiBarChart2, FiPieChart, FiTrendingUp } from 'react-icons/fi';

export const recentFiles = [
  { id: 1, title: 'Q4 2023 Income Statement', type: 'Income Statement', date: '2023-12-31', imageUrl: 'https://i.imgur.com/3SoVl2A.png' },
  { id: 2, title: 'Annual Balance Sheet', type: 'Balance Sheet', date: '2024-01-15', imageUrl: 'https://i.imgur.com/sSctTM2.png' },
  { id: 3, title: 'January 2024 Cash Flow', type: 'Cash Flow', date: '2024-02-05', imageUrl: 'https://i.imgur.com/bM4f2d3.png' },
  { id: 4, title: 'Tax Return FY2023', type: 'Tax Documents', date: '2024-03-20', imageUrl: 'https://i.imgur.com/lPzmrD6.png' },
];

export const categories = [
    { id: 1, name: 'Income Statement', count: 45, icon: <FiFileText size={20} /> },
    { id: 2, name: 'Balance Sheet', count: 30, icon: <FiBarChart2 size={20} /> },
    { id: 3, name: 'Cash Flow', count: 38, icon: <FiPieChart size={20} /> },
    { id: 4, name: 'Tax Documents', count: 12, icon: <FiTrendingUp size={20} /> },
];

export const dashboardStats = {
  revenue: '$187,450',
  avgRevenue: '$8,230',
  profit: '$15,120',
};

export const reportData = {
    title: "Q3 2024 Financial Report",
    executiveSummary: "The third quarter of 2024 saw significant growth in revenue, driven by strong market demand and successful product launches. Net income increased by 15% compared to the previous quarter, reflecting effective cost management and operational efficiencies.",
    incomeStatement: [
        { account: 'Revenue', q1: 150000, q2: 165000, q3: 180000, q4: 195000, total: 690000 },
        { account: 'Cost of Goods Sold', q1: 50000, q2: 55000, q3: 60000, q4: 65000, total: 230000 },
        { account: 'Gross Profit', q1: 100000, q2: 110000, q3: 120000, q4: 130000, total: 460000 },
        { account: 'Operating Expenses', q1: 30000, q2: 32000, q3: 34000, q4: 36000, total: 132000 },
        { account: 'Net Income', q1: 70000, q2: 78000, q3: 86000, q4: 94000, total: 328000 },
    ]
};