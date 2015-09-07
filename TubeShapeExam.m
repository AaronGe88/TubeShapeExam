function [ maxGap ] = TubeShapeExam( design, manufactory)
%UNTITLED Summary of this function goes here
%   Detailed ezeros(rowYBC,4);
    dy = design(:,1);  
    my = manufactory(:, 1);

	[rowYBC, ~] = size(design);
	oneCols = ones(rowYBC,1);
	
	dspts = zeros(rowYBC,4);
	dspts(:,4) = oneCols;
	depts = zeros(rowYBC,4);
	depts(:,2) = -dy;
	depts(:,4) = oneCols;
	
	mspts = zeros(rowYBC,4);
	mspts(:,4) = oneCols;
	mepts = zeros(rowYBC,4);
	mepts(:,2) = -my;
	mepts(:,4) = oneCols;
	
    dtrsf = TransferMat(design);
	dMat = zeros(4,4,rowYBC);
    
    for jj = 1 : rowYBC 
        dMat(:,:,jj) = eye(4,4);
        for ii = rowYBC : -1 : jj 
            dMat(:,:,jj) = dMat(:,:,jj) * dtrsf(:,:,ii);
        end
    end
	dxyz = xyzSection(dMat, dspts, depts);
	
	mtrsf = TransferMat(manufactory);
	mMat = zeros(4,4,rowYBC);
	for jj = 1:rowYBC
		mMat(:,:,jj) = eye(4,4);
		for ii = rowYBC: -1 :jj	
			mMat(:,:,jj) = mMat(:,:,jj) * mtrsf(:,:,ii);
		end
	end
	mxyz = xyzSection(mMat, mspts, mepts);
	
    dline = fitLine(dxyz);
    mline = fitLine(mxyz);
    xlimi = [min(min(dline(:,1)),min(mline(:,1)))-10,max(max(dline(:,1)),max(mline(:,1)))+10];
    ylimi = [min(min(dline(:,2)),min(mline(:,2)))-10,max(max(dline(:,2)),max(mline(:,2)))+10];
    zlimi = [min(min(dline(:,3)),min(mline(:,3)))-10,max(max(dline(:,3)),max(mline(:,3)))+10];
    figure('NumberTitle', 'off', 'Name', 'Íä¹ÜXYZ×ø±êÍ¼');
    hold on;
    plot3(dline(:,1),dline(:,2),dline(:,3),'b*',mline(:,1),mline(:,2),mline(:,3),'rp');
    hold on;
    plot3(dline(:,1),dline(:,2),dline(:,3),'b');
    hold on;
    plot3(mline(:,1),mline(:,2),mline(:,3),'r');
    title('XYZ×ø±ê');
    xlabel('X');  %xÖá
    ylabel('Y');%yÖá
    zlabel('Z');
    xlim(xlimi);
    ylim(ylimi);
    zlim(zlimi);
    %plot(x,y1,'k:',x,y2,,x1,y3,'rp');
    maxGap = dline - mline;
end

function [transfers] = TransferMat(ybc)
	[rows, ~] = size(ybc);
	y = ybc(:, 1);
    b = ybc(:, 2);
    c = ybc(:, 3);
	r = ybc(:, 4);
	
	A1 = zeros(4,4,rows);
	A2 = zeros(4,4,rows);
	A31 = zeros(4,4,rows);
	A32 = zeros(4,4,rows);
	A33 = zeros(4,4,rows);
	A3t = zeros(4,4,rows);
    A3 = zeros(4,4,rows);
	for ii = 1 : rows
		A1(:,:,ii) = eye(4,4);
		A2(:,:,ii) = eye(4,4);
		A31(:,:,ii) = eye(4,4);
		A32(:,:,ii) = eye(4,4);
		A33(:,:,ii) = eye(4,4);
	end
	A1(2,4,:) = y;
	A2(1,1,:) = cosd(b);
	A2(1,3,:) = sind(b);
	A2(3,1,:) = -sind(b);
	A2(3,3,:) = cosd(b);
	
	A31(1,4,:) = -r;
	A32(1,1,:) = cosd(c);
	A32(1,2,:) = sind(c);
	A32(2,1,:) = -sind(c);
	A32(2,2,:) = cosd(c);
	
	A33(1,4,:) = r;
	for ii = 1 : rows
		A3t(:,:,ii) = A33(:,:,ii) * A32(:,:,ii);
	end
	
	for ii = 1 : rows
		A3(:,:,ii) = A3t(:,:,ii) * A31(:,:,ii);
	end
	
	transfers = zeros(4,4,rows);
	for ii = 1 : rows
		transfers(:,:,ii) = A3(:,:,ii) * A2(:,:,ii) * A1(:,:,ii);
	end
	
end

function [xyz] = xyzSection(TMat,spts, epts)
	[rows,~]=size(spts);
	seg = zeros(2,4,rows);
	for ii = 1 : rows
		seg(1,:,ii) = TMat(:,:,ii) * spts(ii,:)';
		seg(2,:,ii) = TMat(:,:,ii) * epts(ii,:)';
	end
	%xyz = seg(:,1:3);
	xyz = seg;
end
	
function [line] = fitLine(xyz)
	vectors = xyz(1,1:3,:) - xyz(2,1:3,:);
	[~,~,rows] = size(xyz);
	% normals = zeros(rows - 1,3);
	% for ii = 1 : rows - 1
		% normals(ii,:) = cross(vectors(1,:,ii),vectors(1,:,ii+1));
		% normals(ii,:) = normals(ii,:) / norm(normals(ii,:));
    % end
    % line = normals;
	line = zeros(rows + 1,3);
	line(1,:) = xyz(1,1:3,1);
	for ii = 1 : rows - 1
		x1 = xyz(1,1,ii);
		y1 = xyz(1,2,ii);
		z1 = xyz(1,3,ii);
		x2 = xyz(2,1,ii+1);
		y2 = xyz(2,2,ii+1);
		z2 = xyz(2,3,ii+1);
        m1 = vectors(1,1,ii);
		m2 = vectors(1,1,ii + 1);
		n1 = vectors(1,2,ii);
		n2 = vectors(1,2,ii + 1);
		p1 = vectors(1,3,ii);
		p2 = vectors(1,3,ii + 1);
		A1 = det([n1,p1;n2,p2]);
		B1 = det([p1,m1;p2,m2]);
		C1 = det([m1,n1;m2,n2]);
		A2 = det([n2,B1;p2,C1]);
		B2 = det([p2,C1;m2,A1]);
		C2 = det([m2,A1;n2,B1]);
		delta1 = det([A1,B1,C1;A2,B2,C2;n1,-m1,0]);
		D1 = A2 * (x2 - x1) + B2 * (y2 - y1) + C2 * (z2 - z1);
		Gx = x1 - D1 * m1 * C1 / delta1;
		Gy = y1 - D1 * n1 *C1 / delta1;
		Gz = z1 + D1 * (A1*m1 +B1 * n1) / delta1;
		
		A3 = n1 * C1 + p1 * det([m1,p1;m2,p2]);
		B3 = p1 * A1 + m1 * det([n1,m1;n2,m2]);
		C3 = m1 * B1 + n1 * det([p1,n1;p2,n2]);	
		delta2 = n2 * det([B1,C1;B3,C3]) + m2 * det([A1,C1;A3,C3]);
		D2 = A3 * (x1 - x2) + B3 * (y1 - y2) + C3 * (z1 - z2);
		
		Hx = x2 - D2 * m2 * C1 / delta2;
		Hy = y2 - D2 * n2 * C1 / delta2;
		Hz = z2 + D2 * (A1 * m2 + B1 * n2) / delta2;
		line(ii + 1,:) = [(Gx + Hx) / 2, (Gy + Hy) /2, (Gz + Hz) / 2];
	end
	line(rows + 1,:) = xyz(2,1:3,rows);
end