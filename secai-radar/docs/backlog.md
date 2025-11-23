# SecAI Radar - Backlog

## Next Features

### 1. Control Detail Page
- **Route**: `/tenant/:id/controls/:controlId`
- **Features**:
  - Capability breakdown visualization
  - "Why" overlays explaining coverage scores
  - Show strongest covering tool per capability
  - Evidence panel with attachments

### 2. Evidence Upload
- **API Endpoints**:
  - `POST /api/tenant/:id/evidence/:controlId` - Upload evidence file
  - `GET /api/tenant/:id/evidence/:controlId` - List evidence files
  - Blob SAS helper for secure uploads
- **UI**:
  - File upload component in Control Detail page
  - Evidence list with preview/download links
  - Drag-and-drop support

### 3. Catalog Editor
- **Routes**:
  - `/admin/catalog/tools` - Edit tool capabilities and strengths
  - `/admin/catalog/controls` - Edit control requirements
- **Features**:
  - CRUD interface for tool strengths
  - CRUD interface for control→capability mappings
  - Validation against schemas
  - Audit trail for changes

### 4. Role-Based Tenant Scoping
- **Features**:
  - Entra ID role claims integration
  - Tenant access control (users can only access assigned tenants)
  - Admin role for cross-tenant access
  - Tenant selector based on user permissions
- **Implementation**:
  - Update `staticwebapp.config.json` with role-based routes
  - Add tenant filtering in API endpoints
  - UI tenant switcher with filtered list

