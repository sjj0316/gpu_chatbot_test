import { NavLink, useMatch } from "react-router";
import {
  Home,
  KeyRound,
  Settings,
  ChevronDown,
  MessageCircle,
  FolderOpen,
  FileText,
  Search,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarRail,
} from "@/shared/ui/sidebar";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/shared/ui/collapsible";
import { cn } from "@/shared/lib/utils";

type MenuItem = {
  id: string;
  label: string;
  path: string;
  icon?: React.ReactNode;
  disabled?: boolean;
};

type MenuGroup = {
  id: string;
  label: string;
  collapsible?: boolean;
  showGroupLabel?: boolean;
  items: MenuItem[];
};

const menuGroups: MenuGroup[] = [
  {
    id: "home",
    label: "홈",
    collapsible: false,
    showGroupLabel: false,
    items: [{ id: "dashboard", label: "홈", path: "/", icon: <Home className="h-4 w-4" /> }],
  },
  {
    id: "chat",
    label: "채팅",
    collapsible: true,
    showGroupLabel: true,
    items: [
      { id: "chat", label: "대화하기", path: "/chat", icon: <MessageCircle className="h-4 w-4" /> },
    ],
  },
  {
    id: "rag",
    label: "지식 저장소 관리",
    collapsible: true,
    showGroupLabel: true,
    items: [
      {
        id: "collection",
        label: "컬렉션 관리",
        path: "/collections",
        icon: <FolderOpen className="h-4 w-4" />,
      },
      {
        id: "documents",
        label: "문서 관리",
        path: "/documents",
        icon: <FileText className="h-4 w-4" />,
      },
      { id: "search", label: "문서 검색", path: "/search", icon: <Search className="h-4 w-4" /> },
    ],
  },
  {
    id: "ai-keys",
    label: "모델 관리",
    collapsible: true,
    showGroupLabel: true,
    items: [
      {
        id: "model-keys",
        label: "모델 API 키 관리",
        path: "/model-keys",
        icon: <KeyRound className="h-4 w-4" />,
      },
    ],
  },
  {
    id: "mcp-servers",
    label: "MCP 서버",
    collapsible: true,
    showGroupLabel: true,
    items: [
      {
        id: "mcp-servers",
        label: "MCP 서버 관리",
        path: "/mcp-servers",
        icon: <Settings className="h-4 w-4" />,
      },
    ],
  },
];

function MenuLink({ item }: { item: MenuItem }) {
  const match = useMatch({ path: item.path, end: item.path === "/" });
  const isActive = Boolean(match);

  return (
    <SidebarMenuItem>
      <SidebarMenuButton asChild isActive={isActive}>
        <NavLink
          to={item.path}
          end={item.path === "/"}
          className={cn(
            "flex items-center gap-2",
            item.disabled && "pointer-events-none opacity-50"
          )}
        >
          {item.icon}
          <span>{item.label}</span>
        </NavLink>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}

export function AppSidebar() {
  return (
    <Sidebar className="overflow-auto pt-16 pb-12" variant="sidebar" collapsible="icon">
      <SidebarHeader />

      <SidebarContent>
        {menuGroups.map((group) =>
          group.collapsible === false ? (
            <SidebarGroup key={group.id}>
              {group.showGroupLabel && <SidebarGroupLabel>{group.label}</SidebarGroupLabel>}
              <SidebarGroupContent>
                <SidebarMenu>
                  {group.items.map((item) => (
                    <MenuLink key={item.id} item={item} />
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ) : (
            <Collapsible key={group.id} defaultOpen className="group/collapsible">
              <SidebarGroup>
                <SidebarGroupLabel asChild>
                  <CollapsibleTrigger className="flex w-full items-center">
                    {group.showGroupLabel && (
                      <span className="text-sm font-semibold">{group.label}</span>
                    )}
                    <ChevronDown
                      className={cn(
                        "ml-auto h-4 w-4 transition-transform",
                        "group-data-[state=open]/collapsible:rotate-180"
                      )}
                    />
                  </CollapsibleTrigger>
                </SidebarGroupLabel>
                <CollapsibleContent>
                  <SidebarGroupContent>
                    <SidebarMenu>
                      {group.items.map((item) => (
                        <MenuLink key={item.id} item={item} />
                      ))}
                    </SidebarMenu>
                  </SidebarGroupContent>
                </CollapsibleContent>
              </SidebarGroup>
            </Collapsible>
          )
        )}
      </SidebarContent>

      <SidebarFooter />
      <SidebarRail />
    </Sidebar>
  );
}
