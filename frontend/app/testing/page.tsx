"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Plus,
  FlaskConical,
  Calendar,
  Trash2,
  Sparkles,
  FileText,
  Beaker,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import AppLayout from "../components/AppLayout";
import { useAuth } from "../../hooks/useAuth";
import {
  useProjects,
  useCreateProject,
  useDeleteProject,
  type Project,
} from "../../lib/api/testing";
import {
  createProjectSchema,
  type CreateProjectInput,
} from "../../lib/schemas/project";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
} from "../components/ui/dialog";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { ShineBorder } from "../components/magicui/shine-border";

// Skeleton Loading Card Component
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-xl skeleton" />
        <div className="w-16 h-5 rounded-full skeleton" />
      </div>
      <div className="w-3/4 h-6 mb-3 skeleton" />
      <div className="w-full h-4 mb-2 skeleton" />
      <div className="w-2/3 h-4 mb-6 skeleton" />
      <div className="pt-4 border-t border-slate-100">
        <div className="w-24 h-4 skeleton" />
      </div>
    </div>
  );
}

// Enhanced Empty State Component
function EmptyState({ onCreateClick }: { onCreateClick: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="col-span-full flex flex-col items-center justify-center py-20 bg-gradient-to-b from-white to-slate-50/50 rounded-3xl border border-dashed border-slate-200 relative overflow-hidden"
    >
      {/* Background Decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-gradient-to-br from-blue-100/40 to-teal-100/40 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-gradient-to-tr from-indigo-100/40 to-purple-100/40 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 flex flex-col items-center">
        <div className="empty-state-icon mb-6">
          <Beaker className="w-10 h-10 text-[var(--arvato-blue)]" />
        </div>

        <h3 className="text-xl font-bold text-slate-800 mb-2">
          Keine Testprojekte
        </h3>
        <p className="text-slate-500 text-sm mb-8 text-center max-w-sm">
          Erstelle dein erstes Projekt, um automatisierte Testpläne aus DDDs zu generieren.
        </p>

        <motion.button
          onClick={onCreateClick}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[var(--arvato-blue)] to-[#00D4AA] text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 transition-shadow"
        >
          <Plus className="w-5 h-5" />
          Erstes Projekt erstellen
        </motion.button>
      </div>
    </motion.div>
  );
}

// Premium Project Card Component
function ProjectCard({
  project,
  index,
  onDelete,
  canDelete,
}: {
  project: Project;
  index: number;
  onDelete: (e: React.MouseEvent, id: string, name: string) => void;
  canDelete: boolean;
}) {
  const router = useRouter();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => router.push(`/testing/${project.id}`)}
      className="cursor-pointer"
    >
      <ShineBorder
        borderRadius={20}
        borderWidth={isHovered ? 2 : 0}
        duration={8}
        color={["#0082D9", "#00D4AA", "#0082D9"]}
        className="h-full"
      >
        <div className={`
          relative p-6 h-full
          bg-gradient-to-br from-white via-white to-slate-50/50
          rounded-[20px]
          transition-all duration-300
          ${isHovered ? 'shadow-premium-hover' : 'shadow-premium'}
        `}>
          {/* Gradient top bar on hover */}
          <div className={`
            absolute top-0 left-0 right-0 h-1 rounded-t-[20px]
            bg-gradient-to-r from-[var(--arvato-blue)] to-[#00D4AA]
            transition-opacity duration-300
            ${isHovered ? 'opacity-100' : 'opacity-0'}
          `} />

          {/* Delete button - Always visible on hover if user has permission */}
          <AnimatePresence>
            {isHovered && canDelete && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.15 }}
                onClick={(e) => onDelete(e, project.id, project.name)}
                className="absolute top-4 right-4 p-2.5 bg-white/90 hover:bg-red-50 text-red-500 hover:text-red-600 rounded-xl backdrop-blur-sm transition-all shadow-lg border border-red-200/50 z-20 hover:scale-110"
                title="Projekt löschen"
              >
                <Trash2 className="w-4 h-4" />
              </motion.button>
            )}
          </AnimatePresence>
          
          {/* Alternative: Always visible delete button in footer if no hover */}
          {!isHovered && canDelete && (
            <button
              onClick={(e) => onDelete(e, project.id, project.name)}
              className="absolute bottom-4 right-4 p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-60 hover:opacity-100 z-10"
              title="Projekt löschen"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Icon */}
          <div className="flex items-start justify-between mb-5">
            <motion.div
              animate={{ rotate: isHovered ? 10 : 0 }}
              transition={{ duration: 0.3 }}
              className={`
                p-3.5 rounded-2xl
                bg-gradient-to-br from-blue-50 to-teal-50
                ${isHovered ? 'shadow-lg shadow-blue-500/10' : ''}
                transition-shadow duration-300
              `}
            >
              <FlaskConical className="w-6 h-6 text-[var(--arvato-blue)]" />
            </motion.div>

            {project.auto_description && (
              <span className="badge-glass flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                AI
              </span>
            )}
          </div>

          {/* Title */}
          <h3 className={`
            font-bold text-lg mb-2 transition-colors duration-300 line-clamp-1
            ${isHovered ? 'text-[var(--arvato-blue)]' : 'text-slate-800'}
          `}>
            {project.name}
          </h3>

          {/* Description */}
          <p className="text-slate-500 text-sm mb-6 line-clamp-2 h-10 leading-relaxed">
            {project.auto_description || project.description || "Keine Beschreibung"}
          </p>

          {/* Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-100/80">
            <div className="flex items-center text-xs font-medium text-slate-400">
              <Calendar className="w-3.5 h-3.5 mr-1.5" />
              {new Date(project.created_at).toLocaleDateString("de-DE", {
                day: "2-digit",
                month: "short",
                year: "numeric",
              })}
            </div>

            {project.test_plan && (
              <span className="flex items-center gap-1 text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                <FileText className="w-3 h-3" />
                Plan
              </span>
            )}
          </div>
        </div>
      </ShineBorder>
    </motion.div>
  );
}

export default function TestingPage() {
  const router = useRouter();
  const { canCreateProject, canDeleteProject } = useAuth();

  // TanStack Query hooks
  const { data: projects = [], isLoading } = useProjects();
  const createMutation = useCreateProject();
  const deleteMutation = useDeleteProject();

  // Modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{
    id: string;
    name: string;
  } | null>(null);

  // React Hook Form for create project
  const form = useForm<CreateProjectInput>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
    },
  });

  const handleCreateProject = async (data: CreateProjectInput) => {
    try {
      await createMutation.mutateAsync(data);
      setShowCreateModal(false);
      form.reset();
    } catch (error) {
      console.error("Failed to create project", error);
    }
  };

  const confirmDeleteProject = (
    e: React.MouseEvent,
    id: string,
    name: string
  ) => {
    e.stopPropagation();
    e.preventDefault();
    setDeleteTarget({ id, name });
    setShowDeleteModal(true);
  };

  const executeDeleteProject = async () => {
    if (!deleteTarget) return;
    try {
      await deleteMutation.mutateAsync(deleteTarget.id);
    } catch (error) {
      console.error("Failed to delete", error);
    } finally {
      setShowDeleteModal(false);
      setDeleteTarget(null);
    }
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-hidden">
        {/* Premium Header */}
        <div className="relative mb-8 pb-6">
          {/* Background decoration */}
          <div className="absolute -top-20 -left-20 w-72 h-72 bg-gradient-to-br from-blue-100/30 to-teal-100/30 rounded-full blur-3xl pointer-events-none" />

          <div className="relative flex justify-between items-start">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="p-2.5 bg-gradient-to-br from-[var(--arvato-blue)] to-[#00D4AA] rounded-xl shadow-lg shadow-blue-500/20">
                  <FlaskConical className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">
                    Testing
                  </h1>
                  <p className="text-slate-500 text-sm">
                    Automatisierte Testplan-Erstellung aus DDDs
                  </p>
                </div>
              </div>
            </div>

            {canCreateProject && (
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-gradient-to-r from-[var(--arvato-blue)] to-[var(--arvato-blue-dark)] hover:from-[var(--arvato-blue-dark)] hover:to-[var(--arvato-blue)] text-white shadow-lg shadow-blue-500/20 border-0 gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Neues Projekt
                </Button>
              </motion.div>
            )}
          </div>

          {/* Stats bar */}
          {!isLoading && projects.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-4 mt-6"
            >
              <div className="stat-card flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <FlaskConical className="w-4 h-4 text-[var(--arvato-blue)]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-800">{projects.length}</p>
                  <p className="text-xs text-slate-500">Projekte</p>
                </div>
              </div>
              <div className="stat-card flex items-center gap-3">
                <div className="p-2 bg-emerald-50 rounded-lg">
                  <FileText className="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-800">
                    {projects.filter(p => p.test_plan).length}
                  </p>
                  <p className="text-xs text-slate-500">Mit Testplan</p>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Content Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6 overflow-y-auto pb-10">
            {[...Array(8)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <EmptyState onCreateClick={() => setShowCreateModal(true)} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6 overflow-y-auto pb-10">
            {projects.map((project: Project, index) => (
              <ProjectCard
                key={project.id}
                project={project}
                index={index}
                onDelete={confirmDeleteProject}
                canDelete={canDeleteProject}
              />
            ))}
          </div>
        )}

        {/* Create Modal with Radix Dialog - Premium Styling */}
        <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
          <DialogContent className="!rounded-2xl !p-0 overflow-hidden !max-w-md">
            <form onSubmit={form.handleSubmit(handleCreateProject)}>
              {/* Gradient header */}
              <div className="bg-gradient-to-r from-[var(--arvato-blue)] to-[#00D4AA] p-6">
                <DialogHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/20 backdrop-blur-sm rounded-xl">
                      <Plus className="w-5 h-5 text-white" />
                    </div>
                    <DialogTitle className="!text-white !text-xl">Neues Projekt</DialogTitle>
                  </div>
                </DialogHeader>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <Label htmlFor="name" className="text-slate-700 font-medium">
                    Projektname
                  </Label>
                  <Input
                    id="name"
                    placeholder="z.B. Payment Service Update"
                    {...form.register("name")}
                    autoFocus
                    className="mt-1.5 !rounded-xl !border-slate-200 focus:!border-[var(--arvato-blue)] focus:!ring-[var(--arvato-blue)]/20"
                  />
                  {form.formState.errors.name && (
                    <p className="text-red-500 text-sm mt-1">
                      {form.formState.errors.name.message}
                    </p>
                  )}
                </div>
              </div>

              <DialogFooter className="!px-6 !py-4 bg-slate-50 border-t border-slate-100">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setShowCreateModal(false)}
                  className="!rounded-xl"
                >
                  Abbrechen
                </Button>
                <Button
                  type="submit"
                  isLoading={createMutation.isPending}
                  disabled={!form.formState.isValid}
                  className="!rounded-xl bg-gradient-to-r from-[var(--arvato-blue)] to-[var(--arvato-blue-dark)] hover:from-[var(--arvato-blue-dark)] hover:to-[var(--arvato-blue)] border-0"
                >
                  Projekt erstellen
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Modal - Premium Styling */}
        <Dialog
          open={showDeleteModal}
          onOpenChange={(open) => {
            setShowDeleteModal(open);
            if (!open) setDeleteTarget(null);
          }}
        >
          <DialogContent className="!rounded-2xl !p-0 overflow-hidden !max-w-md">
            <DialogHeader className="p-6 pb-4">
              <div className="flex items-center gap-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", duration: 0.5 }}
                  className="w-14 h-14 bg-gradient-to-br from-red-100 to-red-50 rounded-2xl flex items-center justify-center shadow-lg shadow-red-500/10"
                >
                  <Trash2 className="w-7 h-7 text-red-500" />
                </motion.div>
                <div>
                  <DialogTitle className="!text-xl">Projekt löschen?</DialogTitle>
                  <p className="text-sm text-slate-500 mt-0.5">
                    Diese Aktion kann nicht rückgängig gemacht werden.
                  </p>
                </div>
              </div>
            </DialogHeader>

            <div className="px-6 pb-4">
              <div className="bg-gradient-to-r from-slate-50 to-slate-100/50 rounded-xl p-4 border border-slate-100">
                <p className="text-sm font-semibold text-slate-700 truncate">
                  {deleteTarget?.name}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Projekt und alle zugehörigen Daten werden gelöscht
                </p>
              </div>
            </div>

            <DialogFooter className="!px-6 !py-4 bg-slate-50 border-t border-slate-100">
              <Button
                variant="ghost"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteTarget(null);
                }}
                className="!rounded-xl"
              >
                Abbrechen
              </Button>
              <Button
                onClick={executeDeleteProject}
                isLoading={deleteMutation.isPending}
                className="!rounded-xl bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 border-0 shadow-lg shadow-red-500/20"
              >
                Löschen
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
